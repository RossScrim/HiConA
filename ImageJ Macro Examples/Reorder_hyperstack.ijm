#@ String preImagePath
#@ String imagePath
#@ String wellPath

open(preImagePath);
imageID = getImageID();

waitForUser("Click OK to continue");

// Input own code here

imageName = getTitle();

run("Split Channels");
run("Merge Channels...", "c1=C2-"+imageName+" c2=C1-"+imageName+" create");

waitForUser("Click OK to continue");

// End of your code
selectImage(imageID);