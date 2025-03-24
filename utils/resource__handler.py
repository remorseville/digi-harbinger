import os
import sys


class ResourceHandler:
    def __init__(self, base_path=None):
        """
        Initialize the ResourceHandler.

        Args:
            base_path (str, optional): Custom base path. If not provided, it will be determined dynamically.
        """
        self.base_path = base_path if base_path else self._get_default_base_path()

    def _get_default_base_path(self):
        """
        Determine the default base path based on whether the app is packaged or in development mode.

        Returns:
            str: The base path.
        """
        return sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath(".")

    def resource_path(self, relative_path):
        """
        Get the full path to a resource based on the relative path.

        Args:
            relative_path (str): The relative path to the resource.

        Returns:
            str: The full path to the resource.
        """
        return os.path.join(self.base_path, relative_path)
    

ResourceHandler = ResourceHandler()