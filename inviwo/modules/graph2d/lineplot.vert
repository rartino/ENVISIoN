
#include "utils/structs.glsl"
#include "utils/pickingutils.glsl"

layout(location = 7) in uint in_PickId;

uniform GeometryParameters geometry;
uniform CameraParameters camera;

uniform vec4 overrideColor;

uniform bool pickingEnabled = false;

out vec4 worldPosition_;
out vec3 normal_;
out vec3 viewNormal_;
out vec4 color_;
out vec3 texCoord_;
flat out vec4 pickColor_;
 
void main() {
#ifdef OVERRIDE_COLOR_BUFFER
    color_ = overrideColor;
#else
    color_ = in_Color;
#endif
    texCoord_ = in_TexCoord;
    worldPosition_ = geometry.dataToWorld * in_Vertex;
    normal_ = geometry.dataToWorldNormalMatrix * in_Normal * vec3(1.0);
    viewNormal_ = (camera.worldToView * vec4(normal_,0)).xyz;
    gl_Position = camera.worldToClip * worldPosition_;
    pickColor_ = vec4(pickingIndexToColor(in_PickId), pickingEnabled ? 1.0 : 0.0);
}