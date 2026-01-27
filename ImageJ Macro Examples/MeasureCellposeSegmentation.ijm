#@ String preImagePath
#@ String imagePath
#@ String wellPath

// Becuase of the ROIManager, this script needs to be run in Interactive Mode. Please tick "Interactive" when selecting the ImageJ Macro and Arguments file.
// If you don't want to see the processes, enable batch mode 
setBatchMode(true)

open(preImagePath);
imageID = getImageID();

// Input own code here

getDimensions(width, height, channels, slices, frames);

imageName = substring(imagePath, lastIndexOf(imagePath, File.separator)+1, lastIndexOf(imagePath, "."));
cellposeROI = imageName+"_rois.zip";
cellposeROIPath = wellPath+File.separator+"cellpose"+File.separator+cellposeROI;

resultsPath = wellPath+File.separator+"imagej";

roiManager("Open", cellposeROIPath);

run("Set Measurements...", "area mean standard modal min perimeter shape redirect=None decimal=3");

for (n=1;n<channels+1;n++){
	selectImage(imageID);
	Stack.setChannel(n);
	roiManager("Measure");

	saveAs("Results", resultsPath+File.separator+"results_"+imageName+"_ch"+n+".csv");	
	
	run("Clear Results");
}

// End of your code
selectImage(imageID);
