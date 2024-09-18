import os
import readline
from typing import List
from typing import Union

import drawsvg as draw

_input = input
def input(prompt, text=""):
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = _input(prompt)
    readline.set_pre_input_hook()

    return result.strip()

canvas_border = 20
stroke_width = 2
stroke_dasharray="9,5"
beam_height = 20
beam_vertical_spacing = 60


class Force:
    def __init__(self, name:str, convention:bool, value:str, position:float, udl=False, udl_start:float=0, udl_distance:float=0, udl_value:str=""):
        global beam_length_m
        
        self.name: str = name
        self.convention: bool = convention
        self.value: str = value

        if udl:
            self.position: float = float(udl_start+0.5*udl_distance)
        else:
            self.position: float = float(position)
        self.udl: bool = udl
        self.udl_start: float = (float(udl_start)/beam_length_m)
        self.udl_distance:float = (float(udl_distance)/beam_length_m)
        self.udl_value: str = udl_value

class Moment:
    def __init__(self, name, convention, center):
        self.name = name
        self.convention = convention
        self.position = center
        self.value=""
        self.udl = False

class Beam:
    def __init__(self, supports, length=1):
        self.supports = supports
        self.length=length

class TypeNotFound(Exception):
    pass

class Support:
    def __init__(self, support_type, position):
        if support_type not in ["roller", "pin", "cantilever"]:
            raise TypeNotFound

        self.type = support_type
        self.position = position


def draw_force(d, force, beam_length, section_y):
    if force.udl:
        start = force.udl_distance+force.udl_start
        end = force.udl_start

        i = start

        while i >= end:
            draw_force(d, Force("", True, "", i), beam_length, section_y)
            i -= 0.1

        return

    force_line_x_pos = beam_length-(beam_length*force.position) 
    text_x = force_line_x_pos+5

    if force_line_x_pos == beam_length:
        force_line_x_pos -= 10
        text_x -= 35
    elif force_line_x_pos == 0:
        force_line_x_pos += 10
        text_x += 10

    if force_line_x_pos < 10:
        force_line_x_pos = 10
    elif force_line_x_pos > 190:
        force_line_x_pos = 190


    if force.convention:
        d.append(draw.Lines(force_line_x_pos-5, section_y+((beam_vertical_spacing-beam_height)/2)-7, 
                            force_line_x_pos, section_y+(beam_vertical_spacing-beam_height)/2,
                            force_line_x_pos+5, section_y+((beam_vertical_spacing-beam_height)/2)-7,
                            fill="#000000",
                            fill_opacity=0,
                            stroke="red",
                            stroke_width=stroke_width))
        
        d.append(draw.Lines(force_line_x_pos, section_y,
                            force_line_x_pos, section_y+(beam_vertical_spacing-beam_height)/2,
                            stroke="red",
                            stroke_width=stroke_width))

        d.append(draw.Text(force.value if force.value else force.name, 12, text_x, section_y+((beam_vertical_spacing-beam_height)/2)-5, fill="red"))

    else:
        d.append(draw.Lines(force_line_x_pos-5, section_y+((beam_vertical_spacing+beam_height)/2)+7, 
                            force_line_x_pos, section_y+(beam_vertical_spacing+beam_height)/2,
                            force_line_x_pos+5, section_y+((beam_vertical_spacing+beam_height)/2)+7,
                            fill="#000000",
                            fill_opacity=0,
                            stroke="red",
                            stroke_width=stroke_width))
        
        d.append(draw.Lines(force_line_x_pos, section_y+beam_vertical_spacing,
                            force_line_x_pos, section_y+(beam_vertical_spacing+beam_height)/2,
                            stroke="red",
                            stroke_width=stroke_width))

        d.append(draw.Text(force.value if force.value else force.name, 12, text_x, section_y+beam_vertical_spacing-5, fill="red"))

def draw_moment(d, moment, center_x, center_y, radius):
    radius -= 5
    path = draw.Path(stroke="blue", stroke_width=2, fill="#000000", fill_opacity=0)
    d.append(path.M(center_x, center_y-radius).A(radius, radius, rot=0, large_arc=True, sweep=1, ex=center_x, ey=center_y+radius))

    if moment.convention:
        d.append(draw.Lines(center_x+5, center_y-(radius+5),
                 center_x, center_y-radius,
                 center_x+5, center_y-(radius-5),
                 stroke="blue",
                 fill_opacity=0,
                 stroke_width=stroke_width)
                 )
        d.append(draw.Lines(center_x, center_y-radius,
                 stroke="blue",
                 stroke_width=stroke_width)
                 )
        d.append(draw.Text(moment.name,
                           12,
                           center_x+radius+2,
                           center_y+radius-5,
                           fill="blue")
                 )
forces: List[Union[Force,Moment]]= []

print("==== Defining Beam ====")
beam_length_m = float(input("Beam length in m (or 1 if unknown): "))

print()
print("==== Defining Forces ====")

while True:
    try:
        force_name=input("Force name: ")
        force_convention=True if input("Is the force acting downwards? Y/n ", "y") != "n" else False
        force_value=input("Force value: ")

        if input("Is force a UDL? Y/n") not in ["N", "n"]:
            force_udl = True
            udl_start = input("How far from the right-hand side does the UDL start? ")
            udl_distance = input("How far does the UDL extend? ")
            udl_value = input("What is the force of the UDL? ")
            forces.append(Force(force_name,
                                force_convention,
                                force_value,
                                float(udl_start),
                                udl=force_udl,
                                udl_start=float(udl_start), 
                                udl_distance=float(udl_distance), 
                                udl_value=udl_value
                                )
                          )
        else: 
            force_position=input("Distance from right-hand side? ")
            forces.append(Force(force_name, force_convention, force_value, float(force_position)))
    except KeyboardInterrupt:
        print()

        break

supports = [
        Support('cantilever', 0),
        ]
"""
for i, support in enumerate(supports):
    if support.type == "cantilever":
        forces.append(Moment(f"M{i+1}",
                             True,
                             support.position))
    forces.append(Force(f"R{i+1}",
                        False,
                        "",
                        support.position
                        ))
""" 
print(f"{len(forces)} forces defined.")

canvas_x = 190 
beam_length = canvas_x*0.8
canvas_y = beam_vertical_spacing*(len(forces)+1)
d = draw.Drawing(canvas_x, canvas_y, origin=(-10,-10))

beam = Beam(supports)

# Draw supports
"""
for support in beam.supports:
    if support.type == "cantilever":
        d.append(draw.Lines(canvas_x*0.8, beam_vertical_spacing,
                            canvas_x*0.8, 0,
                            stroke = "black",
                            stroke_width=stroke_width,
                            ))

        for i in range(int(beam_vertical_spacing/6), beam_vertical_spacing, int(beam_vertical_spacing/6)):
            d.append(draw.Lines(canvas_x*0.8, i,
                                (canvas_x*0.8)+int(beam_vertical_spacing/6), i-int(beam_vertical_spacing/6),
                                stroke_width=stroke_width,
                                stroke="black"))

"""
# Draw forces
"""
for force in forces:
    if not force.name.startswith("R") and not force.name.startswith("M"):
        draw_force(d, force, beam_length, 0)
"""

"""
# Draw beam
d.append(draw.Lines(0, (beam_vertical_spacing-beam_height)/2,
                    0, (beam_vertical_spacing+beam_height)/2,
                    (canvas_x*0.8), (beam_vertical_spacing+beam_height)/2,
                    (canvas_x*0.8), (beam_vertical_spacing-beam_height)/2,
                    close=True,
                    fill = "white",
                    stroke_width=stroke_width,
                    stroke="black",
                    ))
"""

# Start defining sections

sections = []

forces = sorted(forces, key=lambda x: x.position, reverse = True)

for i, force in enumerate([force for force in forces[:-1] if force.position!=0]):
    this_force = force.position
    next_force = forces[i+1].position
    midpoint = (this_force+next_force)/2
    print(f"Making cut between {this_force} and {next_force} at {midpoint}")
    midpoint_px = beam_length - (beam_length * int(beam_length_m/midpoint))


    sections.append((midpoint_px, midpoint, beam.length-this_force, beam.length-next_force,))

# Draw the beam, but replace joints with reaction forces

d.append(draw.Lines(0, (beam_vertical_spacing-beam_height)/2,
                    0, (beam_vertical_spacing+beam_height)/2,
                    (canvas_x*0.8), (beam_vertical_spacing+beam_height)/2,
                    (canvas_x*0.8), (beam_vertical_spacing-beam_height)/2,
                    close=True,
                    fill = "white",
                    stroke_width=stroke_width,
                    stroke="black",
                    ))

for force in forces:
    if isinstance(force, Moment):
        draw_moment(d, force, beam_length-5, 1.5*beam_vertical_spacing, beam_vertical_spacing/3)
    else:
        draw_force(d, force, beam_length, beam_vertical_spacing)

for i, section in enumerate(sections):
    section_y = beam_vertical_spacing*(i+1)
    d.append(draw.Text(f"{round(section[2],2)}<x<{round(section[3], 2)}",
                       8,
                       section[0]/2,
                       section_y+beam_vertical_spacing-5,
                       fill="black",
                       text_anchor="middle",
                       ))
    d.append(draw.Lines(section[0], section_y+beam_vertical_spacing/3,
                        0, section_y+beam_vertical_spacing/3,
                        0, section_y+(beam_vertical_spacing*(2/3)),
                        section[0], section_y+(beam_vertical_spacing*(2/3)),
                        stroke="black",
                        fill="#000000",
                        fill_opacity=0,
                        stroke_width=stroke_width))
    d.append(draw.Lines(section[0], beam_vertical_spacing,
                        section[0], beam_vertical_spacing*(i+3),
                        stroke = "black",
                        stroke_width = 1,

                        stroke_dasharray = stroke_dasharray))

    for force in forces:
        if force.position > section[1]:
            if force.value == "":
                force.value = input(f"Force {force.name} has value ", force.value)
            draw_force(d, force, beam_length, section_y)

    q = Force("Q", True, "", section[1]-0.05 )
    draw_force(d, q, beam_length, section_y+(beam_vertical_spacing/3))
    draw_moment(d,
                Moment("M",
                       True,
                       (section[0]+10, section_y+(0.5*beam_vertical_spacing))
                       ),
                section[0]+10,
                section_y+(0.5*beam_vertical_spacing),
                beam_vertical_spacing/3,
                )


d.set_pixel_scale(10)

pngs = [file for file in os.listdir('.') if file.startswith("pyfbd") and file.endswith("png")]
i = len(pngs)+1
print(f"pyfbd{i}.png")
d.save_png(f"pyfbd{i}.png")
