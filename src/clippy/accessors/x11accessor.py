"""Provides compatibility with the X11 window manager."""

from collections.abc import Callable, Iterable

import Xlib
import Xlib.display
import Xlib.protocol.event

from clippy.accessors.accessor import Accessor
from clippy.clipboard import ClipboardTarget
from clippy.clipsources.clipsource import ClipSource


class X11Accessor(Accessor):
    """Holds information about the current clipboard and its operation."""

    def __init__(self, clipsources: list[ClipSource]) -> None:
        """Create a new accessor compatible with the X11 window system."""
        super().__init__(clipsources)
        self.display = Xlib.display.Display()
        self.window = self.display.screen().root.create_window(
            0,
            0,
            10,
            10,
            0,
            Xlib.X.CopyFromParent,
        )

        def _ga(atom: str) -> int:
            return self.display.get_atom(atom)

        self.TARGET_ATOM_MAP = {
            ClipboardTarget.PLAINTEXT: Xlib.Xatom.STRING,
            ClipboardTarget.GNOME_COPIED_FILES: _ga("x-special/gnome-copied-files"),
            ClipboardTarget.TIMESTAMP: _ga("TIMESTAMP"),
            ClipboardTarget.URI_LIST: _ga("text/uri-list"),
        }

    def get_available_targets(self) -> Iterable[ClipboardTarget]:
        """Return an iterable with every selection target currently supported."""
        return (target for source in self._sources for target in source.targets)

    def write_to_clipboard(
        self,
        targets: Iterable[ClipboardTarget] | None = None,
    ) -> None:
        """Fill the clipboard with values from the sources."""
        # If target whitelist is empty, use every target available
        if targets is None:
            targets = set()
            targets.update(target for s in self._sources for target in s.targets)

        # Map each desired target to a single source
        target_source_map = dict.fromkeys(targets)
        for source in self._sources:
            for source_target in source.targets:
                if source_target in target_source_map:
                    target_source_map[source_target] = source

        # Left over targets are flagged as erroneous
        lost_targets = [t for t, source in target_source_map.items() if not source]
        if lost_targets:
            self._logger.error("Got clipboard target without source for a value.")
            errmsg = f"No source for target(s): {lost_targets}"
            raise ValueError(errmsg)

        # Write the target and its associated source's value to the clipboard
        ts: list[ClipboardTarget] = []
        cs: list[ClipSource] = []
        for t, c in target_source_map.items():
            if t is not None and c is not None:
                ts.append(t)
                cs.append(c)
        self._provide_clipboard_values(
            ts,
            (lambda i=i, c=c: c.get_value(ts[i]) for i, c in enumerate(cs)),
        )

    def _request_x11_clipboard_target_atoms(self) -> list[str]:
        """Return a list of available targets in the external clipboard."""
        data_atom = self.display.get_atom("SEL_DATA")
        sel_atom = self.display.get_atom("CLIPBOARD")
        target_atom = self.display.get_atom("TARGETS")
        window = self.window

        # The data_atom should not be set according to ICCCM, and since
        # this is a new window that is already the case here.

        # Ask for the selection.  We shouldn't use X.CurrentTime, but
        # since we don't have an event here we have to.
        window.convert_selection(sel_atom, target_atom, data_atom, Xlib.X.CurrentTime)

        # Wait for the notification that we got the selection
        while True:
            e = self.display.next_event()
            if e.type == Xlib.X.SelectionNotify:
                break
        response = window.get_full_property(
            data_atom,
            Xlib.X.AnyPropertyType,
            sizehint=10000,
        )
        return [self.display.get_atom_name(v) for v in response.value]

    def _provide_clipboard_values(
        self,
        targets: Iterable[ClipboardTarget],
        contents: Iterable[Callable[[], bytes]],
    ) -> None:
        d = self.display
        w = self.window
        targets_atom = d.get_atom("TARGETS")

        # And to grab the selection we must have a timestamp, get one with
        # a property notify when we're anyway setting wm_name
        w.change_attributes(event_mask=Xlib.X.PropertyChangeMask)
        w.set_wm_name("test")
        e = d.next_event()
        sel_time = e.time
        sel_atom = d.get_atom("CLIPBOARD")
        w.change_attributes(event_mask=0)

        # Grab the selection and make sure we actually got it
        w.set_selection_owner(sel_atom, sel_time)
        if d.get_selection_owner(sel_atom) != w:
            self._logger.error("could not take ownership of {%s}", "CLIPBOARD")
            return

        self._logger.error("took ownership of selection {%s}", "CLIPBOARD")
        types = {
            self.TARGET_ATOM_MAP[t]: v for t, v in zip(targets, contents, strict=True)
        }

        # The event loop, waiting for and processing requests
        while True:
            e = d.next_event()

            if (
                e.type == Xlib.X.SelectionRequest
                and e.owner == w
                and e.selection == sel_atom
            ):
                client = e.requestor

                if e.property == Xlib.X.NONE:
                    self._logger.warning("request from obsolete client!")
                    client_prop = e.target  # per ICCCM recommendation
                else:
                    client_prop = e.property

                target_name = d.get_atom_name(e.target)

                self._logger.info(
                    "got request for {%s}, dest {%s} on 0x{%s}, {%s}",
                    target_name,
                    d.get_atom_name(client_prop),
                    client.id,
                    client.get_wm_name(),
                )

                prop_type = None
                prop_format = None
                prop_value = None
                # Is the client asking for which types we support?
                if e.target == targets_atom:
                    # Then respond with TARGETS and the type
                    prop_value = [targets_atom, *types.keys()]
                    prop_type = Xlib.Xatom.ATOM
                    prop_format = 32

                # Request for the offered type
                elif e.target in types:
                    prop_value = types[e.target]()
                    prop_type = e.target
                    prop_format = 8

                # Something else, tell client they can't get it
                else:
                    self._logger.warning("refusing conversion to {%s}", target_name)
                    client_prop = Xlib.X.NONE

                # Put the data on the dest window, if possible
                if client_prop != Xlib.X.NONE:
                    client.change_property(
                        client_prop,
                        prop_type,
                        prop_format,
                        prop_value,
                    )

                # And always send a selection notification
                ev = Xlib.protocol.event.SelectionNotify(
                    time=e.time,
                    requestor=e.requestor,
                    selection=e.selection,
                    target=e.target,
                    property=client_prop,
                )

                client.send_event(ev)

            elif (
                e.type == Xlib.X.SelectionClear and e.window == w and e.atom == sel_atom
            ):
                self._logger.error("lost ownership of selection {%s}", "CLIPBOARD")
                return

            # A proper owner would also look for PropertyNotify here on
            # the selector's windows to implement INCR and waiting for
            # acknowledgement that the client has finished copying.
