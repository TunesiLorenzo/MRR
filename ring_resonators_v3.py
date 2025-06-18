import gdsfactory as gf
from collections.abc import Sequence
import numpy as np
import os


# ========================
# Parameters and Constants
# ========================
class LadderMrr:
    def __init__(self, component=None, gaps=[[2,5,2],[10,2,10]], radii=[[150,100],[100,150]], coupling_length=20, vertical_length=[40,80],
                stage_distance=400, wg_width=0.5, heater_width=4, phase_line_offset=50,
                num_pads=10, pad_size=76, pad_tolerance=2, pad_spacing=100, pad_clearance=2600, 
                layer_heater=(2,0), layer_wg=(1,0), layer_routing=(12,0),
                fiberarray_clearance=500, fiberarray_spacing=100):

        self.component = component

        self.gaps = gaps
        self.radii = radii
        self.coupling_length = coupling_length
        self.vertical_length = vertical_length

        self.stage_distance = stage_distance
        self.wg_width = wg_width
        self.heater_width = heater_width
        self.phase_line_offset = phase_line_offset

        self.num_pads = num_pads
        self.pad_size = pad_size
        self.pad_tolerance = pad_tolerance
        self.pad_spacing = pad_spacing
        self.pad_clearance = pad_clearance

        self.layer_heater = layer_heater
        self.layer_wg = layer_wg
        self.layer_routing = layer_routing

        self.fiberarray_clearance = fiberarray_clearance
        self.fiberarray_spacing = fiberarray_spacing

        self.electrical_contacts = []
        self.optical_contacts = []

    def create_structure(self):

        self.add_rings()
        self.add_circular_heaters()
        self.add_phase_line()
        pad_array=self.add_pads()
        self.route_electrical(pad_array_ex=pad_array)
        self.route_optical()

        self.component.movex(-self.stage_distance/2)

    def add_rings(self): # adds the four rings and main ports
        r1 = self.component << gf.components.ring_crow(gaps=self.gaps[0], radius=self.radii[0], ring_cross_sections=('strip', 'strip', 'strip'), length_x=self.coupling_length, lengths_y=self.vertical_length, cross_section='strip')
        r2 = self.component << gf.components.ring_crow(gaps=self.gaps[1], radius=self.radii[1], ring_cross_sections=('strip', 'strip', 'strip'), length_x=self.coupling_length, lengths_y=self.vertical_length, cross_section='strip')
        r3 = self.component << gf.components.straight(length=self.stage_distance, cross_section='strip')

        r1.connect("o3", r3.ports["o1"])
        r2.connect("o4", r3.ports["o2"])

        self.optical_contacts.append(r1["o1"])
        self.optical_contacts.append(r2["o2"])

        self.component.add_port("input", port=r1.ports["o2"])
        self.component.add_port("drop", port=r1.ports["o4"])
        self.component.add_port("through", port=r2.ports["o1"])
        self.component.add_port("add", port=r2.ports["o3"])


    def add_phase_line(self): # adds the delay line (2 S bends and straight section) and respective heater
        offset = 2*(sum(self.radii[0])-sum(self.radii[1])) + (sum(self.gaps[0])-sum(self.gaps[1]))
        xs_metal = gf.cross_section.heater_metal(width=self.heater_width, layer=self.layer_heater)
        
        bend1 = self.component << gf.components.bend_s(size=tuple([self.phase_line_offset, self.phase_line_offset]),cross_section="strip")
        bend2 = self.component << gf.components.bend_s(size=tuple([self.phase_line_offset, -self.phase_line_offset - offset]),cross_section="strip")
        bend_h1 = self.component << gf.components.bend_s(size=tuple([self.phase_line_offset, self.phase_line_offset]),cross_section=xs_metal)
        bend_h2 = self.component << gf.components.bend_s(size=tuple([self.phase_line_offset, -self.phase_line_offset - offset]),cross_section=xs_metal)
        s = self.component << gf.components.straight(length=self.stage_distance-2*self.phase_line_offset, cross_section='strip')
        h = self.component << gf.components.straight(length=self.stage_distance-2*self.phase_line_offset, cross_section=xs_metal)

        bend1.connect("o1",self.optical_contacts[0])
        s.connect("o1",bend1["o2"])
        bend2.connect("o1",s["o2"])

        bend_h1.connect("e1",self.optical_contacts[0],allow_width_mismatch=True,allow_layer_mismatch=True,allow_type_mismatch=True)
        h.connect("e1",bend_h1["e2"])
        bend_h2.connect("e1",h["e2"])

        c1 = self.component << gf.components.rectangle(size=(10, 10), layer=self.layer_routing)
        c1.connect("e3",bend_h1["e1"],allow_width_mismatch=True,allow_layer_mismatch=True)
        c1.move([10, (10-self.heater_width)/2])

        c2 = self.component << gf.components.rectangle(size=(10, 10), layer=self.layer_routing)
        c2.connect("e1",bend_h2["e2"],allow_width_mismatch=True,allow_layer_mismatch=True)
        c2.move([-10, (10-self.heater_width)/2])

        self.electrical_contacts[4:4]=[c1["e2"],c2["e2"]]



    def add_pads(self):
        pad_array_in = self.component << gf.components.pad_array("pad", columns=self.num_pads, column_pitch=self.pad_spacing, port_orientation=270, size=(self.pad_size, self.pad_size), centered_ports=False)
        pad_array_ex = self.component << gf.components.pad_array("pad", columns=self.num_pads, column_pitch=self.pad_spacing, port_orientation=270, size=(self.pad_size + 2 * self.pad_tolerance, self.pad_size + 2 * self.pad_tolerance), centered_ports=False)

        for pad_array in (pad_array_in, pad_array_ex):
            pad_array.movex(-self.num_pads / 2 * self.pad_spacing + self.pad_size / 2 )
            pad_array.movey(self.pad_clearance)
        return pad_array_ex
    
    def add_circular_heaters(self): 
        xs_metal = gf.cross_section.heater_metal(width=self.heater_width, layer=self.layer_heater)
        self.radii = [row[::-1] for row in self.radii]
        self.vertical_length = self.vertical_length[::-1]

        contact_offset=[[-10,10],[-10,10]]
        for n_stage in range(2):
            for n_ring in range(2):
                b = gf.components.bend_circular(width=self.heater_width, radius=self.radii[n_stage][n_ring], cross_section=xs_metal)
                sh = gf.components.straight(width=self.heater_width, length=self.coupling_length, cross_section=xs_metal)
                sv = gf.components.straight(width=self.heater_width, length=self.vertical_length[n_ring], cross_section=xs_metal)

                offset_x = - (self.coupling_length + 2*self.radii[n_stage][0])
                offset_y = self.radii[n_stage][0] + self.wg_width + self.gaps[n_stage][0]

                if n_ring == 1:
                    offset_x =- (self.coupling_length + sum(self.radii[n_stage]))
                    offset_y += self.radii[n_stage][0] + self.radii[n_stage][1] + self.vertical_length[0] +self.vertical_length[1] + self.wg_width + self.gaps[n_stage][1]
                if n_stage == 1:
                    offset_x *= -1
                    offset_x += self.stage_distance

                if n_stage == 0 and n_ring==0:
                    bh1 = self.component.add_ref(b)
                    bh1.rotate(-90)
                    bh2 = self.component.add_ref(b)
                    sh1 = self.component.add_ref(sh)
                    sh2 = self.component.add_ref(sv)
                
                elif n_stage == 1 and n_ring==0: 
                    bh1 = self.component.add_ref(b)
                    bh1.rotate(-90)
                    bh1.mirror_x(0)
                    bh2 = self.component.add_ref(b).mirror_x(0)
                    sh1 = self.component.add_ref(sh).mirror_x(0)
                    sh2 = self.component.add_ref(sv).mirror_x(0)

                elif n_stage == 1 and n_ring==1: 
                    bh1 = self.component.add_ref(b)
                    bh1.rotate(-90)
                    bh1.mirror_x(0)
                    bh2 = self.component.add_ref(b).mirror_x(0)
                    sh1 = self.component.add_ref(sh).mirror_x(0)
                    sh2 = self.component.add_ref(sv).mirror_x(0)
                    bh1.mirror_y(0)
                    bh2.mirror_y(0)
                    sh1.mirror_y(0)
                    sh2.mirror_y(0)

                elif n_stage == 0 and n_ring==1: 
                    bh1 = self.component.add_ref(b)
                    bh1.rotate(-90)
                    bh1.mirror_y(0)
                    bh2 = self.component.add_ref(b).mirror_y(0)
                    sh1 = self.component.add_ref(sh).mirror_y(0)
                    sh2 = self.component.add_ref(sv).mirror_y(0)

                bh1.movex(offset_x)
                bh1.movey(offset_y) 

                sh1.connect("e1", bh1.ports["e2"])
                bh2.connect("e1", sh1.ports["e2"])
                sh2.connect("e1", bh2.ports["e2"])

                s1_1 = self.component << gf.components.rectangle(size=(10, 10), layer=self.layer_routing)
                s1_1.connect("e4",bh1["e1"], allow_width_mismatch=True, allow_layer_mismatch=True)

                s1_2 = self.component << gf.components.rectangle(size=(10, 10), layer=self.layer_routing)
                s1_2.connect("e2",sh2["e2"],allow_width_mismatch=True,allow_layer_mismatch=True)
                
                s1_1.move([-(10-self.heater_width)/2,contact_offset[n_stage][n_ring]])
                s1_2.move([-(10-self.heater_width)/2,contact_offset[n_stage][n_ring]])
                
                if n_stage == n_ring:
                    self.electrical_contacts.append(s1_1["e1"])
                    self.electrical_contacts.append(s1_2["e3"])
                else:
                    self.electrical_contacts.append(s1_2["e1"])
                    self.electrical_contacts.append(s1_1["e3"])

        tmp_dmp=self.electrical_contacts[-2:]
        self.electrical_contacts[-2:]=self.electrical_contacts[-4:-2]
        self.electrical_contacts[-4:-2]=tmp_dmp

    def route_electrical(self,pad_array_ex):
        gf.routing.route_bundle(
            self.component,
            ports1 = self.electrical_contacts,
            ports2 = list(pad_array_ex.ports),
            separation=15,
            start_straight_length=50,
            end_straight_length=1,
            # bend=gf.components.wire_corner,
            cross_section="metal_routing",
            allow_width_mismatch=True,
            # router= "electrical",
            # sort_ports=True,
            auto_taper = False,
        )

    def route_optical(self):

        gdspath = os.path.join(os.getcwd(), "ANT_GC.GDS")
        antgc = gf.read.import_gds(gdspath)

        my_route_s = gf.cross_section.strip(
            width=self.wg_width,                # same as route_width=5
            layer=self.layer_wg           # same as your original routing_layer usage
        )

        antgc.add_port(
            "o1",
            center=(antgc.x, antgc.y - 19.95),
            orientation=270,
            width=self.wg_width,
            layer=self.layer_wg,
            )

        grating_number = 6

        for i in range(grating_number):
            antgc_ref = self.component << antgc.copy()
            
            antgc_ref.dmove(   # con dmove puoi spostare nel punto desiderato al posto che move "relativo"
            origin=(antgc_ref.x, antgc_ref.y), # .x e .y ritornano il centro del componente
            destination=( -self.fiberarray_clearance, ((-1.5+i)*self.fiberarray_spacing) +250))
            antgc_ref.drotate(angle=90, center=antgc_ref.center)

            shadow_rect = self.component << gf.components.rectangle(size=(0.5, 0.5), layer=self.layer_wg, port_type="optical") # needed because add port is broken as of 9.7.0
            shadow_rect.connect("o3", antgc_ref["o1"]),
            self.component.add_port(f"Grating{i}", port=shadow_rect["o1"])

        routes = gf.routing.route_bundle(
            component=self.component,
            ports1 = [self.component.ports["input"], self.component.ports["drop"], self.component.ports["through"], self.component.ports["add"]],#, self.component.ports["input"]],
            ports2 = [self.component.ports["Grating1"],self.component.ports["Grating2"],self.component.ports["Grating3"],self.component.ports["Grating4"]],#, self.component.ports["Grating1"]],
            cross_section=my_route_s,
            allow_width_mismatch=True,
            on_collision="show_error",
            sort_ports=True,
            separation=5,
            auto_taper = False
        )

        bend1 = self.component << gf.components.bend_circular(radius = 15, angle = -180)
        bend1.connect("o1",self.component["Grating0"])
        straight1 = self.component << gf.components.straight(length=50,cross_section=my_route_s)
        straight1.connect("o1",bend1["o2"])

        bend2 = self.component << gf.components.bend_circular(radius = 15, angle = 180)
        bend2.connect("o1",self.component["Grating5"])
        straight2 = self.component << gf.components.straight(length=50,cross_section=my_route_s)
        straight2.connect("o1",bend2["o2"])

        gf.routing.route_single(component=self.component, port1=straight1["o2"], port2=straight2["o2"], cross_section=my_route_s)





gaps = [[2, 5, 2], [10, 2, 10]]
radii = [[150, 100], [100, 150]]
coupling_length = 20
vertical_length = [40, 80]

stage_distance = 400
wg_width = 0.5
heater_width = 4
phase_line_offset = 50




# Create instance of the class with these parameters

master_component = gf.Component("MRRLadder")
MRR= LadderMrr(
    component=master_component,
    gaps=gaps,
    radii=radii,
    coupling_length=coupling_length,
    vertical_length=vertical_length,
    stage_distance=stage_distance,
    wg_width=wg_width,
    heater_width=heater_width,
    phase_line_offset=phase_line_offset,
    fiberarray_clearance=600
)


MRR.create_structure()
master_component.draw_ports()
master_component.write_gds(f"ring_resonators.gds")


