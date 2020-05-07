# Name: Bandstructure3DNetworkHandler 
import sys,os,inspect
import inviwopy as ivw
import inviwopy.glm as glm
import h5py
import numpy as np

app = ivw.app
network = app.network

factory = app.processorFactory

from envisionpy.processor_network.NetworkHandler import NetworkHandler

class Bandstructure3DNetworkHandler(NetworkHandler):
    def __init__(self, hdf5_path, inviwoApp):
        NetworkHandler.__init__(self, inviwoApp)
        self.setup_bandstructure_network(hdf5_path)


    def processorInfo():
        return ivw.ProcessorInfo(
            classIdentifier = "org.inviwo.Bandstructure3DNetworkHandler", 
            displayName = "Bandstructure3DNetworkHandler",
            category = "Python",
            codeState = ivw.CodeState.Stable,
            tags = ivw.Tags.PY
        )

    def getProcessorInfo(self):
        return Bandstructure3DNetworkHandler.processorInfo()
    
    def initializeResources(self):
        print("init")

    def setup_bandstructure_network(self, h5file):
        #Extractiong network metadata
        with h5py.File(h5file, 'r') as f:
            KPoints = f.get('BandStructure').get('KPoints').value
            Symbols = f.get('Highcoordinates')
            length_iteration = len(KPoints)#number of iterations
            sym_list = []
            kpoint_list = []
            iteration_list = []
            sym_it_list = []
            for x in range(len(Symbols)):
                sym_list.append(
                    f.get('Highcoordinates').get(str(x)).get('Symbol').value
                )
                kpoint_list.append(
                    f.get('Highcoordinates').get(str(x)).get('Coordinates').value
                )
        
                for i in range(len(KPoints)):
                    if np.array_equal(KPoints[i],kpoint_list[x]):
                        iteration_list.append(i)
                        sym_it_list.append(f.get('Highcoordinates').get(str(x)).get('Symbol').value)

        #HDF5Source
        hdf5_source = factory.create('org.inviwo.hdf5.Source', glm.ivec2(0, 0))
        hdf5_source.identifier = 'hdf5 source'
        hdf5_source.filename.value = h5file
        network.addProcessor(hdf5_source)


        #HDF5PathSelection
        hdf5_path_selection = factory.create('org.inviwo.hdf5.PathSelection', glm.ivec2(0,75))
        hdf5_path_selection.identifier = 'band'
        hdf5_path_selection.selection.value = '/Bandstructure/Bands'#detta är datan som vi vill ha ut ur hdf5 filen
        network.addProcessor(hdf5_path_selection)

        network.addConnection(
            hdf5_source.getOutport('outport'), 
            hdf5_path_selection.getInport('inport')
        )

        #HDF5PathSelectionAllChildren
        hdf5_path_selection_all_children = factory.create('org.inviwo.HDF5PathSelectionAllChildren', glm.ivec2(0,150))
        hdf5_path_selection_all_children.identifier = 'All'
        network.addProcessor(hdf5_path_selection_all_children)

        network.addConnection(
            hdf5_path_selection.getOutport('outport'), 
            hdf5_path_selection_all_children.getInport('hdf5HandleInport')
        )


        #HDF5ToFunction
        hdf5_to_function = factory.create('org.inviwo.HDF5ToFunction', glm.ivec2(0, 225))
        hdf5_to_function.identifier = 'Convert to function'
        network.addProcessor(hdf5_to_function)

        network.addConnection(
            hdf5_path_selection_all_children.getOutport('hdf5HandleVectorOutport'),
            hdf5_to_function.getInport('hdf5HandleFlatMultiInport')
        )

#FunctionToDataframe
        function_to_dataframe = factory.create('org.inviwo.FunctionToDataFrame',glm.ivec2(0,300))
        function_to_dataframe.identifier = 'Function to dataframe'
        network.addProcessor(function_to_dataframe)

        network.addConnection(
            hdf5_to_function.getOutport('functionVectorOutport'),
            function_to_dataframe.getInport('functionFlatMultiInport')
        )

#LinePlot
        line_plot = factory.create('org.inviwo.LinePlotProcessor',glm.ivec2(0,375))
        line_plot.identifier = 'Line Plot'
        line_plot.getPropertyByIdentifier('allYSelection').value = True
        line_plot.getPropertyByIdentifier('enable_line').value = True
        line_plot.getPropertyByIdentifier('show_x_labels').value = False
        network.addProcessor(line_plot)

        network.addConnection(
            function_to_dataframe.getOutport('dataframeOutport'),
            line_plot.getInport('dataFrameInport')
        )


#2DMeshRenderer
        mesh_render = factory.create('org.inviwo.Mesh2DRenderProcessorGL', glm.ivec2(0,450))
        mesh_render.identifier = 'Render'
        network.addProcessor(mesh_render)

        network.addConnection(
            line_plot.getOutport('outport'),
            mesh_render.getInport('inputMesh')
        )
        network.addConnection(
            line_plot.getOutport('labels'),
            mesh_render.getInport('imageInport')
        )


#Background
        background = factory.create('org.inviwo.Background',glm.ivec2(0,525))
        background.identifier = 'Background'
        network.addProcessor(background)

        background.bgColor1.value = ivw.glm.vec4(1)
        background.bgColor2.value = ivw.glm.vec4(1)

        network.addConnection(
            mesh_render.getOutport('outputImage'),
            background.getInport('inport')
        )

#TextOverlay
        text_overlay = factory.create('org.inviwo.TextOverlayGL',glm.ivec2(0,600))
        text_overlay.identifier = 'Text overlay GL'
        network.addProcessor(text_overlay)

        text_overlay.font.fontSize.value = 20
        text_overlay.position.value = ivw.glm.vec2(0.43, 0.93)
        text_overlay.color.value = ivw.glm.vec4(0,0,0,1)
        text_overlay.text.value = 'Energy [eV]'

        network.addConnection(
            background.getOutport('outport'),
            text_overlay.getInport('inport')
        )

#SecondTextOverlay
        second_text_overlay = factory.create('org.inviwo.TextOverlayGL',glm.ivec2(0,675))
        second_text_overlay.identifier = 'Text overlay GL'
        network.addProcessor(second_text_overlay)

        second_text_overlay.font.fontSize.value = 20
        second_text_overlay.position.value = ivw.glm.vec2(0.35, 0.02)
        second_text_overlay.color.value = ivw.glm.vec4(0,0,0,1)
        second_text_overlay.text.value = 'Critical points in the brillouin zone'

        network.addConnection(
            text_overlay.getOutport('outport'),
            second_text_overlay.getInport('inport')
        )


#DrawSymbols
        overlay_list = []
        mul_iteration = 0.8/len(KPoints)
        x_coord_list = []

        for q in range(len(sym_it_list)):
            third_text_overlay = factory.create('org.inviwo.TextOverlayGL',glm.ivec2(200*q,750))

            network.addProcessor(third_text_overlay)
            third_text_overlay.font.fontSize.value = 20
            x_cor = (mul_iteration*iteration_list[q]) + 0.1
            third_text_overlay.position.value = ivw.glm.vec2(x_cor, 0.06)
            third_text_overlay.color.value = ivw.glm.vec4(0,0,0,1)
            third_text_overlay.text.value = sym_it_list[q]
            overlay_list.append(third_text_overlay)
            x_coord_list.append(x_cor)    

        network.addConnection(
            second_text_overlay.getOutport('outport'),
            overlay_list[0].getInport('inport')
        )


        for w in range(1,(len(overlay_list))-1):
            network.addConnection(
               overlay_list[w-1].getOutport('outport'),
               overlay_list[w].getInport('inport')
            )

        network.addConnection(
            overlay_list[w].getOutport('outport'),
            overlay_list[w+1].getInport('inport')
        )

#DrawLinesToEverySymbol
        line_list = []

        for r in range(0, len(sym_it_list)):
            line_plot = factory.create('org.inviwo.LinePlotProcessor',glm.ivec2(200*r,375))
            line_plot.getPropertyByIdentifier('allYSelection').value = True
            line_plot.getPropertyByIdentifier('enable_line').value = True
            line_plot.getPropertyByIdentifier('line_x_coordinate').minValue = 0
            line_plot.getPropertyByIdentifier('line_x_coordinate').maxValue = length_iteration

            network.addProcessor(line_plot)
            line_plot.getPropertyByIdentifier('line_x_coordinate').value = iteration_list[r]
            line_list.append(line_plot)
            network.addConnection(
                function_to_dataframe.getOutport('dataframeOutport'),
                line_list[r].getInport('dataFrameInport')
            )
            network.addConnection(
                line_plot.getOutport('outport'),
                mesh_render.getInport('inputMesh')
            ) 


#Canvas
        canvas = factory.create('org.inviwo.CanvasGL', glm.ivec2(0,825))
        canvas.identifier = 'Canvas'
        network.addProcessor(canvas)

        network.addConnection(
            third_text_overlay.getOutport('outport'),
            canvas.getInport('inport')
        )


        canvas.inputSize.dimensions.value = ivw.glm.ivec2(900, 825)
        hdf5_path_selection.selection.value = '/Bandstructure/Bands'








       
