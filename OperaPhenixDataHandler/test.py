macro = """
        openPath(path);
        filter();
        save();
        """

arg = {"arg1": 1,
       "arg2": "hej"}


macro = """
        @ String preImagePath 
        @ String postImagePath""" + macro

arg["preImagePath"] = "path1"
arg["postImagePath"] = "path2"

print(macro, arg)