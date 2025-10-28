import importlib
import os
import warnings

from aider.dump import dump  # noqa: F401

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

AIDER_SITE_URL = "https://aider.chat"
AIDER_APP_NAME = "Aider"

os.environ["OR_SITE_URL"] = AIDER_SITE_URL
os.environ["OR_APP_NAME"] = AIDER_APP_NAME
os.environ["LITELLM_MODE"] = "PRODUCTION"

# `import litellm` takes 1.5 seconds, defer it!

VERBOSE = False


class LazyLiteLLM:
    _lazy_module = None
    _lazy_classes = {
        "ModelResponse": "ModelResponse",
        "Choices": "Choices",
        "Message": "Message",
    }

    def __getattr__(self, name):
        # Check if the requested attribute is one of the explicitly lazy-loaded classes
        if name in self._lazy_classes:
            self._load_litellm()
            class_name = self._lazy_classes[name]
            return getattr(self._lazy_module, class_name)

        # Handle other attributes (like `acompletion`) as before
        if name == "_lazy_module":
            return super()
        self._load_litellm()
        return getattr(self._lazy_module, name)

    def _load_litellm(self):
        if self._lazy_module is not None:
            return

        self._lazy_module = importlib.import_module("litellm")
        self._lazy_module.suppress_debug_info = True
        self._lazy_module.turn_off_message_logging = True
        self._lazy_module.set_verbose = False
        self._lazy_module.drop_params = True
        self._lazy_module._logging._disable_debugging()


litellm = LazyLiteLLM()

__all__ = [litellm]
