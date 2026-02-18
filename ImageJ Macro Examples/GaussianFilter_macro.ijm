#@ String preImagePath
#@ String imagePath
#@ String wellPath

// Input own variables here
#@ int sigmaVal
#@ float satVal

open(preImagePath);
imageID = getImageID();

// Input own code here

run("Gaussian Blur...", "sigma=sigmaVal");

// End of your code

selectImage(imageID);
