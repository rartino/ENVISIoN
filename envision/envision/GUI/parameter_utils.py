
import inviwopy
import inspect

app = inviwopy.app
network = app.network

def charge_add_tf_point(value, color):
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    tf_property.add(value, color)

def charge_clear_tf():
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    tf_property.clear()

def charge_get_points():
    Raycaster = network.getProcessorByIdentifier('Charge raycaster')
    tf_property = Raycaster.isotfComposite.transferFunction
    return [[x.pos, x.color] for x in tf_property.getValues()]

def print_all_processors():
    #inspect.getmembers(network, predicate=inspect.ismethod)
    #print(network.getProcessors())