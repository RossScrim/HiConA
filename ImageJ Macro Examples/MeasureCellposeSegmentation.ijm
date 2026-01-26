#@ String preImagePath
#@ String imagePath
#@ String wellPath

open(preImagePath);
imageID = getImageID();

// Input own code here

getDimensions(width, height, channels, slices, frames);

imageName = substring(imagePath, lastIndexOf(imagePath, File.separator)+1, lastIndexOf(imagePath, "."));
cellposeROI = imageName+"_rois.zip";
cellposeROIPath = wellPath+File.separator+"cellpose"+File.separator+cellposeROI;
print(imageName);
print(cellposeROI);
print(cellposeROIPath);

resultsPath = wellPath+File.separator+"imagej";

roiManager("Open", cellposeROIPath);

run("Set Measurements...", "area mean standard modal min perimeter shape redirect=None decimal=3");

for (n=1;n<channels+1;n++){
	Stack.setChannel(n);
	roiManager("Measure");

	saveAs("Results", resultsPath+File.separator+"results_"+imageName+"_ch"+n+".csv");	
	run("Clear Results");
}

// End of your code
selectImage(imageID);
