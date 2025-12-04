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
        binning = int(self.tree.find('.//ns:Experiment/ns:Exposures/ns:Exposure/ns:SimpleChannel/ns:CameraSetting/ns:BinningX', self.ns).text)
        M_objective = int(self.tree.find('.//ns:Experiment/ns:Exposures/ns:Exposure/ns:ObjectiveMagnification', self.ns).text)
        M_factor = 1.87 #From observation and manual calculations

        return (camera_px_size*binning)/(M_objective*M_factor) #um

    def get_channel_order(self):
        return [channel.text for channel in self.tree.findall('.//ns:Sequence/ns:Record/ns:Channel', self.ns)]
    
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
        print(fields)
        
        with open(file, 'w') as f:
            f.write('\n'.join(top_text))
            f.write('\n')

            for i, field in enumerate(fields):
                image_name = well_name+'f'+str(i+1).zfill(2)
                x = field[0]/self.pixel_size
                y = -field[1]/self.pixel_size # Inverted for ImageJ Stitching

                f.write(image_name+'.tif'+f'; ; ({x}, {y})\n')

        f.close()
    

if __name__ == '__main__':
    test_file = r"Z:\Emma\hs\bb41dbf0-41ce-4913-ac11-9a37ce70c088\bb41dbf0-41ce-4913-ac11.xml"

    XMLReader = XMLConfigReader(test_file)

    print(XMLReader.get_channel_order())

    well_layout = XMLReader.get_well_layout()
    #print(well_layout)
    XMLReader.generate_TileConfiguration(well_layout=well_layout, well_name="r04c05", output_dir=r"Z:\Emma\Stitching test processed\18112025_LS411N_ATX968_S9.6 - 1\r04c05")

