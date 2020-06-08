from src.core.state import State
from src.core.callbacks import Callback, CallbackOrder


class AssignTarget(Callback):
    signature = "fe"
    order = CallbackOrder.MIDDLE

    def on_fe_end(self, state: State):
        dataframes = state.dataframes
        for key, df in dataframes.items():
            if state.target_name in df.columns:
                state.logger.info(
                    f"Found target `{state.target_name}` in {key}")
                state.target = df[state.target_name].values
                break
