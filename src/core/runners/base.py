from typing import List, Optional

from src.core import State
from src.core.callbacks import Callback


class SubRunner:
    signature = ""
    group = "main"

    def __init__(self, config: dict, state: State):
        self.config = config
        self.state = state
        self.callbacks: List[Callback] = []

    def _run_callbacks(self, phase="start", signature: Optional[str] = None):
        assert phase in {"start", "end"}

        signature = self.signature if signature is None else signature
        method = "on_" + signature + "_" + phase

        # add user defined callbacks
        callbacks_in_group = self.state.callbacks.get(self.group)
        if callbacks_in_group is None:
            user_defined_callbacks = None
        else:
            user_defined_callbacks = self.state.callbacks[self.group].get(
                signature)

        callbacks = self.callbacks
        if user_defined_callbacks is not None:
            preset_callback_names = [
                callback.__class__.__name__ for callback in callbacks
            ]
            for callback in user_defined_callbacks:
                if callback.__class__.__name__ in preset_callback_names:
                    # overwrite
                    index = preset_callback_names.index(
                        callback.__class__.__name__)
                    callbacks[index] = callback
                else:
                    callbacks.append(callback)

        for callback in sorted(callbacks):
            callback.__getattribute__(method)(self.state)

    def run(self):
        raise NotImplementedError
