import imagej
import scyjava
import os

class ImageJSingleton:
    #_instance = None
    _ij = None

    @classmethod
    def get_instance(cls, imagej_loc):
        if cls._ij is None:
            plugins_dir = os.path.join(imagej_loc, "plugins") # Path to Fiji Plugins
            scyjava.config.add_option(f'-Dplugins.dir={plugins_dir}')
            cls._ij = imagej.init(imagej_loc, mode='interactive')
            cls.show_ui(False)
        return cls._ij
        
    @classmethod
    def dispose(cls):
        if cls._ij is not None:
            cls._ij.dispose()
            cls._ij = None
    
    @classmethod
    def show_ui(cls, state):
        WindowManager = scyjava.jimport('ij.WindowManager')
        non_image_titles = WindowManager.getNonImageTitles()

        for title in non_image_titles:
            window = WindowManager.getWindow(title)
            if window:
                window.setVisible(state)