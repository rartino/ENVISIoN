
import inviwopy
import inspect

app = inviwopy.app
network = app.network


#-----------------------------
#--Transfer function editing--

def charge_start_vis():
    pass

def charge_add_tf_point(value, color):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    tf_property.add(value, color)

def charge_clear_tf():
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    tf_property.clear()

def charge_remove_tf_point():
    pass

def charge_get_points():
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    return [[x.pos, x.color] for x in tf_property.getValues()]

#---------------------------
#--Background and lighting--

def charge_set_shading_mode(mode):
    pass

def charge_set_background(color_1 = None, color_2 = None, style = 2):
    pass


def print_all_processors():
    #inspect.getmembers(network, predicate=inspect.ismethod)
    #print(network.getProcessors())
    pass

def charge_toggle_plane(enable):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    pos_indicator = Raycaster.positionindicator
    pos_indicator.plane1.enable.value = True
    pos_indicator.plane2.enable.value = False
    pos_indicator.plane3.enable.value = False
    pos_indicator.enable.value = enable

def charge_set_plane_normal(x, y, z):
    #Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    #plane = Raycaster.positionindicator.plane1
    #plane.normal.value = inviwopy.glm.vec3(x, y, z)

    vol_slice = network.getProcessorByIdentifier('Volume Slice')
    vol_slice.sliceAxis.value = 3
    vol_slice.planeNormal.value = inviwopy.glm.vec3(x, y, z)


def charge_set_plane_height(h):
    pass

