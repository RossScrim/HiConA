#@ String preImagePath
#@ String imagePath
#@ String wellPath

open(preImagePath);
imageID = getImageID();

// Input own code here

title = getTitle();

run("Split Channels");
run("Merge Channels...", "c1=C2-"+imageName+" c2=C1-"+imageName+" create");

// End of your code
selectImage(imageID);