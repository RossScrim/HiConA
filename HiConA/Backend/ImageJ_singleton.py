import os
import imagej
import scyjava


class ImageJSingleton:
    _ij = None

    @classmethod
    def get_instance(cls, imagej_loc):
        if cls._ij is None:
            # Configure plugins before initialization
            plugins_dir = os.path.join(imagej_loc, "plugins")
            scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')

            # headless mode is mandatory for macOS stability
            cls._ij = imagej.init(imagej_loc, mode='')

            # show_ui logic is usually redundant in headless, but kept for compatibility
            cls.show_ui(False)
        return cls._ij

    @classmethod
    def dispose(cls):
        if cls._ij is not None:
            cls._ij.dispose()
            cls._ij = None

    @classmethod
    def show_ui(cls, state):
        try:
            WindowManager = scyjava.jimport('ij.WindowManager')
            non_image_titles = WindowManager.getNonImageTitles()
            if non_image_titles:
                for title in non_image_titles:
                    window = WindowManager.getWindow(title)
                    if window:
                        window.setVisible(state)
        except Exception:
            # In strictly headless environments, UI managers might not be accessible
            pass