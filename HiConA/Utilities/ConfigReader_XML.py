import xml.etree.ElementTree as ET
import os

class XMLConfigReader:
    def __init__(self, file_path):
        self.tree = ET.parse(file_path)
        self.ns = self._get_namespace()
        self.pixel_size = self._get_pixel_size()

    def _get_namespace(self):
        root = self.tree.getroot()
        namespace = root.tag.split('}')[0].strip('{') if '}' in root.tag else ''
        return {'ns':namespace}
    
    def _get_pixel_size(self):
        camera_px_size = float(self.tree.find('.//ns:InstrumentDescription/ns:Cameras/ns:Camera/ns:PixelSizeX', self.ns).text)*(10**6) #um
        try:
            binning = int(self.tree.find('.//ns:Experiment/ns:Exposures/ns:Exposure/ns:SimpleChannel/ns:CameraSetting/ns:BinningX', self.ns).text)
        except:
            binning = int(self.tree.find('.//ns:Experiment/ns:Exposures/ns:Exposure/ns:Record/ns:Channels/ns:Channel/ns:CameraSetting/ns:BinningX', self.ns).text)
        M_objective = int(self.tree.find('.//ns:Experiment/ns:Exposures/ns:Exposure/ns:ObjectiveMagnification', self.ns).text)
        M_factor = 1.087 #From observation and manual calculations

        #print(camera_px_size, binning, M_objective)
        return (camera_px_size*binning)/(M_objective*M_factor) #um

    def get_pixel_scale(self):
        return self.pixel_size
        
    def get_channel_order(self):
        return [channel.text for channel in self.tree.findall('.//ns:Sequence/ns:Record/ns:Channel', self.ns)]
    
    def get_stitching_overlap(self):
        return int(self.tree.find('.//ns:Experiment/ns:Sublayouts/ns:Sublayout/ns:Definition/ns:OverlapX', self.ns).text)
    
    def get_num_planes(self):
        return int(self.tree.find('.//ns:Experiment/ns:Stack/ns:Planes', self.ns).text)
    
    def get_well_layout(self):
        sublayouts = self.tree.findall('.//ns:Experiment/ns:Sublayouts/ns:Sublayout', self.ns)
        wells = self.tree.findall('.//ns:Experiment/ns:MeasurementLayout/ns:Wells/ns:Well', self.ns)

        well_layout = {}

        for well in wells:
            col = well.find('ns:Col', self.ns).text
            row = well.find('ns:Row', self.ns).text

            well_name = "r"+row.zfill(2)+"c"+col.zfill(2)
            sublayout_id = int(well.find('ns:SublayoutID', self.ns).text)

            sublayout = sublayouts[sublayout_id-1]

            fields = sublayout.findall('ns:Field', self.ns)

            field_layout = []
            for field in fields:
                x = float(field.find('ns:X', self.ns).text)*(10**6) #um
                y = float(field.find('ns:Y', self.ns).text)*(10**6) #um
                field_layout.append([x,y])

            well_layout[well_name] = field_layout

        return well_layout
    
    def generate_TileConfiguration(self, well_layout, well_name, output_dir):
        top_text = ['# Define the number of dimensions we are working on', 'dim = 2', '# Define the image coordinates (in pixels)']

        file = os.path.join(output_dir, f'TileConfiguration_{well_name}.txt')
        
        fields = well_layout[well_name]
        #print(fields)
        
        with open(file, 'w') as f:
            f.write('\n'.join(top_text))
            f.write('\n')

            for i, field in enumerate(fields):
                image_name = well_name+'_f'+str(i+1).zfill(2)
                x = field[0]/self.pixel_size
                y = -field[1]/self.pixel_size # Inverted for ImageJ Stitching

                f.write(image_name+'.tiff'+f'; ; ({x}, {y})\n')

        f.close()
    

if __name__ == '__main__':
    test_file = r"Z:\Emma\Opera Phenix Test Data\hs\4e88424a-8346-4ec4-8142-cecbf124b857\4e88424a-8346-4ec4-8142.xml"

    XMLReader = XMLConfigReader(test_file)

    print(XMLReader.get_channel_order())
    print(XMLReader.get_stitching_overlap())
    print(XMLReader.get_num_planes())
    well_layout = XMLReader.get_well_layout()
    #print(well_layout)
    #XMLReader.generate_TileConfiguration(well_layout=well_layout, well_name="r04c05", output_dir=r"Z:\Emma\Stitching test processed\18112025_LS411N_ATX968_S9.6 - 1\r04c05")

