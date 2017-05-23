import inviwo
import os


def _add_processor(id,name,xpos=0,ypos=0):
    new_name = inviwo.addProcessor(id, name)
    inviwo.setProcessorPosition(new_name,(xpos, ypos))
    inviwo.setProcessorSelected(new_name, True)
    return new_name

def _add_h5source(h5file, xpos=0, ypos=0):
    name = os.path.splitext(os.path.basename(h5file))[0]
    if not (name in inviwo.getProcessors()):
        name = _add_processor('org.inviwo.hdf5.Source', name, xpos, ypos)
        inviwo.setPropertyValue(name+'.filename', h5file)
    return name

