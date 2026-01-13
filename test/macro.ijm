#@ String preImagePath
#@ String postImagePath
#@ String orgImagePath
// Input own variables here
#@ int sigmaVal
#@ float satVal

open(preImagePath);

// Input own code here

run("Gaussian Blur...", "sigma=sigmaVal");
//run("Enhance Contrast...", "saturated=satVal normalize");
run("Ice");

// End of your code

saveAs("Tiff", postImagePath);