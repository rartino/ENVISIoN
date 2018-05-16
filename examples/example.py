# This example file is part of the ENVISIoN Electronic structure visualization studio
#
# Load this file into the Inviwo Python Editor (which you can access under the menu Python, 
# which is available if Inviwo has been compiled with the Python module on)
#
# For Copyright and License information see the file LICENSE distributed alongside ENVISIoN
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE 
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os, sys

# Configuration
PATH_TO_ENVISION=os.path.expanduser("~/ENVISIoN/envision")
PATH_TO_VASP_CALC=os.path.expanduser("~/ENVISIoN/data/Cu/1/10")
PATH_TO_HDF5=os.path.expanduser("/tmp/envision_demo.hdf5")


sys.path.insert(0, os.path.expanduser(PATH_TO_ENVISION)) # Or `pip install --editable`.

import envision
import envision.inviwo

#result = envision.parse_all(PATH_TO_HDF5, PATH_TO_VASP_CALC)
#print("Found properties in parse: "+str(result))

#envision.parser.vasp.unitcell(PATH_TO_HDF5, PATH_TO_VASP_CALC)
#envision.parser.vasp.charge(PATH_TO_HDF5, PATH_TO_VASP_CALC)
#envision.parser.vasp.elf(PATH_TO_HDF5, PATH_TO_VASP_CALC)
#envision.parser.vasp.dos(PATH_TO_HDF5, PATH_TO_VASP_CALC)
#envision.parser.vasp.fermi_surface(PATH_TO_HDF5, PATH_TO_VASP_CALC)

xpos=0
envision.inviwo.unitcell(PATH_TO_HDF5, xpos=xpos)
xpos += 400
envision.inviwo.charge(PATH_TO_HDF5, slice=True, xpos=xpos)
xpos += 400
#envision.inviwo.elf(PATH_TO_HDF5, slice=True, xpos=xpos)
xpos += 400
#envision.inviwo.dos(PATH_TO_HDF5, xpos)
xpos += 400
#envision.inviwo.bandstructure(PATH_TO_HDF5, xpos)
xpos += 400

app = inviwopy.app
network = app.network
network.addConnection(network.getProcessorByIdentifier('Unit Cell Renderer').getOutport('image'), network.getProcessorByIdentifier('MeshRenderer').getInport('imageInport'))

network.addLink(network.getProcessorByIdentifier('Unit Cell Renderer').getPropertyByIdentifier('camera'), network.getProcessorByIdentifier('MeshRenderer').getPropertyByIdentifier('camera'))
network.addLink(network.getProcessorByIdentifier('MeshRenderer').getPropertyByIdentifier('camera'), network.getProcessorByIdentifier('Unit Cell Renderer').getPropertyByIdentifier('camera'))

