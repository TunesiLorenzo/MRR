import gdsfactory as gf
from collections.abc import Sequence
import numpy as np
import os


# ========================
# Parameters and Constants
# ========================
gaps1: Sequence[float] = (2,)*3
gaps2: Sequence[float] = (2,)*3
rad1: Sequence[float] = (100,)*2
rad2: Sequence[float] = (100,)*2
coupling_length = 10
distance_between_rings = 200                    # between the center of the strip
vertical_length: Sequence[float] = (40,)*2      #length of the vertical straight parts of the ring
guide_width = 0.5
heater_width = 4

# Pads
num_pads = 10                                   # n. of pads in a row
pad_size = 76
pad_tollerance = 2                              # actual dimension of pad: (pad_size +- pad_tollerance)
pad_spacing = 100                               # distance between pads in a row
distance_optic_pad = 2600                       # distance between pads and optical components

# Layers
LAYER_HEATER = (2, 0)
LAYER_WG = (1, 0)

# Basic component
c = gf.Component()


# ====================
# Ring resonators
# ====================
r1 = c << gf.components.ring_crow(gaps=gaps1, radius=rad1, ring_cross_sections=('strip', 'strip', 'strip'), length_x=coupling_length, lengths_y=vertical_length, cross_section='strip')
r2 = c << gf.components.ring_crow(gaps=gaps2, radius=rad2, ring_cross_sections=('strip', 'strip', 'strip'), length_x=coupling_length, lengths_y=vertical_length, cross_section='strip')
r3 = c << gf.components.straight(length=distance_between_rings, cross_section='strip')
r4 = c << gf.components.straight(length=distance_between_rings, cross_section='strip')

r1.connect("o3", r3.ports["o1"])
r2.connect("o1", r3.ports["o2"])


c.add_port("input", port=r1.ports["o2"])
c.add_port("drop", port=r1.ports["o4"])
c.add_port("through", port=r2.ports["o4"])
c.add_port("add", port=r2.ports["o2"])


# ====================
# Micro heaters
# ====================
# clockwise numerated, starting from bottom left
# sovrapposizione minima con il routing: 5

# def add_heater(name_prefix, x_offset, y_offset, height, orientation):
#     if (orientation == "vertical"):
#         h = c << gf.components.rectangle(size=(heater_width, height), layer=LAYER_HEATER)
#     elif (orientation == "orizzontal"):
#         h = c << gf.components.rectangle(size=(height, heater_width), layer=LAYER_HEATER)
#     h.movex(x_offset)
#     h.movey(y_offset)
#     if (orientation == "vertical"):
#         port1 = c << gf.components.rectangle(size=(heater_width, heater_width), layer=LAYER_HEATER)
#         port1.movex(x_offset)
#         port1.movey(y_offset)
#         port2 = c << gf.components.rectangle(size=(heater_width, heater_width), layer=LAYER_HEATER)
#         port2.movex(x_offset)
#         port2.movey(y_offset-heater_width+height)
#         c.add_port(f"{name_prefix}_1", port=port1.ports["e1"])
#         c.add_port(f"{name_prefix}_2", port=port2.ports["e1"])
#     elif (orientation == "orizzontal"):
#         port1 = c << gf.components.rectangle(size=(heater_width, heater_width), layer=LAYER_HEATER)
#         port1.movex(heater_width)
#         port2 = c << gf.components.rectangle(size=(heater_width, heater_width), layer=LAYER_HEATER)
#         port2.movex(-heater_width)
#         c.add_port(f"{name_prefix}_1", port=port1.ports["e4"])
#         c.add_port(f"{name_prefix}_2", port=port2.ports["e4"])
    
#     return h

# add_heater("h1", - (coupling_length + 2 * rad1[0] + heater_width / 2),
#            rad1[0] + guide_width + gaps1[0], 
#            vertical_length[0], "vertical")
# add_heater("h2", - (coupling_length + 2 * rad1[0] + heater_width / 2),
#            2 * rad1[0] + rad1[1] + 2 * guide_width + gaps1[0] + gaps1[1] + vertical_length[0],
#            vertical_length[1], "vertical")

# h3 = c << gf.components.rectangle(size=(distance_between_rings, heater_width), layer=(2, 0))
# h3.connect("e1", r1.ports["o1"], allow_width_mismatch = True, allow_layer_mismatch = True, allow_type_mismatch=True) 
# c.add_port("h3_1", center=((distance_between_rings), (2*rad1[0] + 2*rad1[1] + gaps1[0] + gaps1[1] + gaps1[2] + 4*guide_width + vertical_length[0] + vertical_length[1])), orientation=90, port_type="electrical", cross_section="metal_routing")
# c.add_port("h3_2", center=(0, (2*rad1[0] + 2*rad1[1] + 3*guide_width + gaps1[0] + gaps1[1] + gaps1[2] + vertical_length[0] + vertical_length[1])), orientation=90, port_type="electrical", cross_section="metal_routing")


# add_heater("h4", coupling_length + 2 * rad2[1] - heater_width / 2 + distance_between_rings,
#            2 * rad2[0] + rad2[1] + 2 * guide_width + gaps2[0] + gaps2[1] + vertical_length[0],
#            vertical_length[1], "vertical")

# add_heater("h5", coupling_length + 2 * rad2[0] - heater_width / 2 + distance_between_rings,
#            rad2[0] + guide_width + gaps2[0],
#            vertical_length[0], "vertical")
contacts_east = [] 
contacts_west = []
contacts_north = []

h1 = c << gf.components.rectangle(size=(heater_width, vertical_length[0]), layer=(2, 0))
h1.movex(- (coupling_length + 2*rad1[0] + heater_width/2))
h1.movey( rad1[0] + guide_width + gaps1[0]) 

# Add top square
s1_1 = c << gf.components.rectangle(size=(10, 10), layer=(12, 0))
s1_1.connect("e4",h1["e2"],allow_width_mismatch=True,allow_layer_mismatch=True)
s1_1.move([-(10-heater_width)/2,-10])
# s1_1.movex(- (coupling_length + 2*rad1[0] + heater_width/2)- 10  + heater_width)
# s1_1.movey( rad1[0] + guide_width + gaps1[0])

# Add bottom square
s1_2 = c << gf.components.rectangle(size=(10, 10), layer=(12, 0))
s1_2.connect("e2",h1["e4"],allow_width_mismatch=True,allow_layer_mismatch=True)
s1_2.move([-(10-heater_width)/2,+10])

contacts_west.append(s1_1["e1"])
contacts_west.append(s1_2["e1"])

#c.add_port(port=s1_2["e1"],name="h1_1")
# c.add_port("h1_1", center=(-(coupling_length + 2*rad1[0] -heater_width/2), (rad1[0] + guide_width + gaps1[0] + vertical_length[0])), orientation=180, port_type="electrical", cross_section="metal_routing")
# c.add_port("h1_2", center=(-(coupling_length + 2*rad1[0] -heater_width/2), (rad1[0] + guide_width + gaps1[0])), orientation=180, port_type="electrical", cross_section="metal_routing")


h2 = c << gf.components.rectangle(size=(heater_width, vertical_length[0]), layer=(2, 0))
h2.movex(- (coupling_length + 2*rad1[0] + heater_width/2))
h2.movey( 2*rad1[0] + rad1[1] + 2*guide_width + gaps1[0] +gaps1[1] + vertical_length[0]) 

# Same procedure for heater 2
s2_1 = c << gf.components.rectangle(size=(10, 10), layer=(12, 0))
s2_1.connect("e4",h2["e2"],allow_width_mismatch=True,allow_layer_mismatch=True)
s2_1.move([-(10-heater_width)/2,-10])
s2_2 = c << gf.components.rectangle(size=(10, 10), layer=(12, 0))
s2_2.connect("e2",h2["e4"],allow_width_mismatch=True,allow_layer_mismatch=True)
s2_2.move([-(10-heater_width)/2,+10])

contacts_west.append(s2_1["e1"])
contacts_west.append(s2_2["e1"])

# c.add_port("h2_2", center=(-(coupling_length + 2*rad1[0] -heater_width/2), (2*rad1[0] + rad1[1] + 2*guide_width + gaps1[0] +gaps1[1] + vertical_length[0] + vertical_length[1])), orientation=180, port_type="electrical", cross_section="metal_routing")
# c.add_port("h2_1", center=(-(coupling_length + 2*rad1[0] -heater_width/2), (2*rad1[0] + rad1[1] + 2*guide_width + gaps1[0] +gaps1[1] + vertical_length[0])), orientation=180, port_type="electrical", cross_section="metal_routing")

h3 = c << gf.components.rectangle(size=(distance_between_rings, heater_width), layer=(2, 0))
h3.connect("e1", r1.ports["o1"], allow_width_mismatch = True, allow_layer_mismatch = True, allow_type_mismatch=True) 

s3_1 = c << gf.components.rectangle(size=(10, 10), layer=(12, 0))
s3_1.connect("e3",h3["e1"],allow_width_mismatch=True,allow_layer_mismatch=True)
s3_1.move([10, (10-heater_width)/2])
s3_2 = c << gf.components.rectangle(size=(10, 10), layer=(12, 0))
s3_2.connect("e1",h3["e3"],allow_width_mismatch=True,allow_layer_mismatch=True)
s3_2.move([-10, (10-heater_width)/2])

contacts_north.append(s3_1["e3"])
contacts_north.append(s3_2["e3"])

# c.add_port("h3_1", center=((distance_between_rings), (2*rad1[0] + 2*rad1[1] + gaps1[0] + gaps1[1] + gaps1[2] + 3*guide_width + vertical_length[0] + vertical_length[1] -heater_width/2)), orientation=90, port_type="electrical", cross_section="metal_routing")
# c.add_port("h3_2", center=(0, (2*rad1[0] + 2*rad1[1] + gaps1[0] + gaps1[1] + gaps1[2] + 3*guide_width + vertical_length[0] + vertical_length[1] -heater_width/2)), orientation=90, port_type="electrical", cross_section="metal_routing")

h4 = c << gf.components.rectangle(size=(heater_width, vertical_length[0]), layer=(2, 0))
h4.movex( coupling_length + 2*rad2[1] - heater_width/2 + distance_between_rings)
h4.movey( 2*rad2[0] + rad2[1] + 2*guide_width + gaps2[0] + gaps2[1] + vertical_length[0]) 

s4_1 = c << gf.components.rectangle(size=(10, 10), layer=(12, 0))
s4_1.connect("e4",h4["e2"],allow_width_mismatch=True,allow_layer_mismatch=True)
s4_1.move([(10-heater_width)/2,-10])
s4_2 = c << gf.components.rectangle(size=(10, 10), layer=(12, 0))
s4_2.connect("e2",h4["e4"],allow_width_mismatch=True,allow_layer_mismatch=True)
s4_2.move([(10-heater_width)/2,+10])

contacts_east.append(s4_1["e3"])
contacts_east.append(s4_2["e3"])


# c.add_port("h4_2", center=((coupling_length + 2*rad1[0] -heater_width/2 + distance_between_rings), (2*rad2[0] + rad2[1] + 2*guide_width + gaps2[0] +gaps2[1] + vertical_length[0] + vertical_length[1])), orientation=0, port_type="electrical", cross_section="metal_routing")
# c.add_port("h4_1", center=((coupling_length + 2*rad1[0] -heater_width/2 + distance_between_rings), (2*rad2[0] + rad2[1] + 2*guide_width + gaps2[0] +gaps2[1] + vertical_length[0])), orientation=0, port_type="electrical", cross_section="metal_routing")

h5 = c << gf.components.rectangle(size=(heater_width, vertical_length[0]), layer=(2, 0))
h5.movex( coupling_length + 2*rad2[0] - heater_width/2 + distance_between_rings)
h5.movey( rad2[0] + guide_width + gaps2[0]) 

s5_1 = c << gf.components.rectangle(size=(10, 10), layer=(12, 0))
s5_1.connect("e4",h5["e2"],allow_width_mismatch=True,allow_layer_mismatch=True)
s5_1.move([(10-heater_width)/2,-10])
s5_2 = c << gf.components.rectangle(size=(10, 10), layer=(12, 0))
s5_2.connect("e2",h5["e4"],allow_width_mismatch=True,allow_layer_mismatch=True)
s5_2.move([(10-heater_width)/2,+10])

contacts_east.append(s5_1["e3"])
contacts_east.append(s5_2["e3"])


# c.add_port("h5_1", center=((coupling_length + 2*rad1[0] -heater_width/2 + distance_between_rings), (rad2[0] + guide_width + gaps2[0] + vertical_length[0])), orientation=0, port_type="electrical", cross_section="metal_routing")
# c.add_port("h5_2", center=((coupling_length + 2*rad1[0] -heater_width/2 + distance_between_rings), (rad2[0] + guide_width + gaps2[0])), orientation=0, port_type="electrical", cross_section="metal_routing")


# ========================
# Centering the component
# ========================
c.movex(-distance_between_rings/2)  


# ====================
# Pads
# ====================
pad_array_in = c << gf.components.pad_array("pad", columns=num_pads, column_pitch=pad_spacing, port_orientation=270, size=(pad_size, pad_size), centered_ports=False)
pad_array_ex = c << gf.components.pad_array("pad", columns=num_pads, column_pitch=pad_spacing, port_orientation=270, size=(pad_size + 2 * pad_tollerance, pad_size + 2 * pad_tollerance), centered_ports=False)

for pad_array in (pad_array_in, pad_array_ex):
    pad_array.movex(-num_pads / 2 * pad_spacing + pad_size / 2 )
    pad_array.movey(distance_optic_pad)



# ====================
# Electrical Routing
# ====================

gf.routing.route_bundle(
    c,
    ports1 = [s1_2["e1"], s1_1["e1"], s2_2["e1"], s2_1["e1"], s3_1["e2"], s3_2["e2"], s4_1["e3"], s4_2["e3"], s5_1["e3"], s5_2["e3"]],
    ports2 = list(pad_array_ex.ports),
    separation=15,
    end_straight_length=1,
    # bend=gf.components.wire_corner,
    cross_section="metal_routing",
    allow_width_mismatch=True,
    # router= "electrical",
    # sort_ports=True,
    auto_taper = False,
)




# ====================
# Optical Routing
# ====================

gdspath = os.path.join(os.getcwd(), "ANT_GC.GDS")
antgc = gf.read.import_gds(gdspath)


my_route_s = gf.cross_section.strip(
    width=0.5,                # same as route_width=5
    layer=(1, 0)           # same as your original routing_layer usage
)

antgc.add_port(
    "o1",
    center=(antgc.x, antgc.y - 19.95),
    orientation=270,
    width=0.5,
    layer=(1, 0),
    )

grating_number = 4
fiberarray_spacing = 100
fiberarray_clearance = 500

for i in range(grating_number):
    antgc_ref = c << antgc.copy()
    
    antgc_ref.dmove(   # con dmove puoi spostare nel punto desiderato al posto che move "relativo"
    origin=(antgc_ref.x, antgc_ref.y), # .x e .y ritornano il centro del componente
    destination=( ((-1.5+i)*fiberarray_spacing) ,    -fiberarray_clearance))
    antgc_ref.drotate(angle=180, center=antgc_ref.center)

    shadow_rect = c << gf.components.rectangle(size=(0.5, 0.5), layer=(1, 0),port_type="optical")
    shadow_rect.connect("o3", antgc_ref["o1"]),
    c.add_port(f"Grating{i}", port=shadow_rect["o1"])

routes = gf.routing.route_bundle(
    component=c,
    ports1 = [c.ports["input"], c.ports["drop"], c.ports["through"], c.ports["add"]],#, c.ports["input"]],
    ports2 = [c.ports["Grating0"],c.ports["Grating1"],c.ports["Grating2"],c.ports["Grating3"]],#, c.ports["Grating1"]],
    cross_section=my_route_s,
    allow_width_mismatch=True,
    on_collision="show_error",
    sort_ports=True,
    separation=5,
    auto_taper = False
)


c.write_gds(f"ring_resonatorsRR.gds")

