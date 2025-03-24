with open("C:/Users/ewestlund/OneDrive - The Institute of Cancer Research/Desktop/Fiji Scripts/BigStitcher_AfterUpdate_macro.ijm", "r") as f:
    macro = f.read()

#macro = """
#        openPath(path);
#        filter();
#        save();
#        """

arg = {"arg1": 1,
       "arg2": "hej",
       "arg3":0.2}

arg["preImagePath"] = "path1"
arg["postImagePath"] = "path2"

print(macro, arg)

arg_text = ""

for key in arg.keys():
    if type(arg[key]) == str:
        arg_text += "@ String " + str(arg[key]) +"\n"
    elif type(arg[key]) == int:
        arg_text += "@ Int " + str(arg[key]) +"\n"
    elif type(arg[key]) == float:
        arg_text += "@ Float " + str(arg[key]) +"\n"

#print(arg_text)

#macro = arg_text + macro

#print(arg_text)


