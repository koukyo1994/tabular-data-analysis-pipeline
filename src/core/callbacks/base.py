from enum import auto, IntEnum

from src.core import State


class CallbackOrder(IntEnum):
    HIGHEST = auto()
    ASSERTION = auto()
    HIGHER = auto()
    MIDDLE = auto()
    LOWER = auto()
    LOWEST = auto()

    def __lt__(self, enum: IntEnum):  # type: ignore
        return self.value > enum.value

    def __gt__(self, enum: IntEnum):  # type: ignore
        return self.value < enum.value

    def __le__(self, enum: IntEnum):  # type: ignore
        return self.value >= enum.value

    def __ge__(self, enum: IntEnum):  # type: ignore
        return self.value <= enum.value


class Callback:
    signature = "base"
    callback_order = CallbackOrder.HIGHEST

    def __lt__(self, callback):
        return self.callback_order > callback.callback_order

    def __gt__(self, callback):
        return self.callback_order < callback.callback_order

    def __le__(self, callback):
        return self.callback_order >= callback.callback_order

    def __ge__(self, callback):
        return self.callback_order <= callback.callback_order

    def on_experiment_start(self, state: State):
        pass

    def on_experiment_end(self, state: State):
        pass

    def on_data_loading_start(self, state: State):
        pass

    def on_data_loading_end(self, state: State):
        pass

    def on_features_start(self, state: State):
        pass

    def on_features_end(self, state: State):
        pass

    def on_preprocess_start(self, state: State):
        pass

    def on_preprocess_end(self, state: State):
        pass

    def on_feature_loading_start(self, state: State):
        pass

    def on_feature_loading_end(self, state: State):
        pass

    def on_split_start(self, state: State):
        pass

    def on_split_end(self, state: State):
        pass

    def on_model_train_start(self, state: State):
        pass

    def on_model_train_end(self, state: State):
        pass

    def on_model_inference_start(self, state: State):
        pass

    def on_model_inference_end(self, state: State):
        pass

    def on_train_fold_start(self, state: State):
        pass

    def on_train_fold_end(self, state: State):
        pass
