import numpy as np # pyright: ignore[reportMissingImports]

class coordinates:
    def __init__(self, ra, dec):
        assert ra >= 0. and ra < 24.0, "RA must be between 0 and 24 hours"
        assert dec >= -180. and dec <= 180., "Dec must be between -180 and 180 degrees"
        self.ra = round(ra,4)
        self.dec = round(dec,4)

        self.original_ra = self.ra
        self.original_dec = self.dec

    def get_position(self):
        return (self.ra, self.dec)

    def get_original_position(self):
        return (self.original_ra, self.original_dec)

    def reset_position(self):
        self.ra = self.original_ra
        self.dec = self.original_dec

    def add_to_dec(self, delta_dec):
        self.dec += delta_dec
        if self.dec > 180:
            self.dec -= 360
        elif self.dec < -180:
            self.dec += 360
        self.dec = round(self.dec,4)

    def add_to_ra(self, delta_ra):
        self.ra += delta_ra
        if self.ra >= 24.0:
            self.ra -= 24.0
        elif self.ra < 0.0:
            self.ra += 24.0
        self.ra = round(self.ra,4)

    # basic move functions
    def move_north(self, distance):
        # making dec more negative moves the object toward the north end of CCD
        self.add_to_dec(-distance)

    def move_south(self, distance):
        # making dec more positive moves the object toward the south end of CCD
        self.add_to_dec(distance)

    def move_east(self, distance):
        # making ra more positive moves the object toward the east end of CCD
        self.add_to_ra(distance)

    def move_west(self, distance):
        # making ra more negative moves the object toward the west end of CCD
        self.add_to_ra(-distance)

    # move to filter positions
    def move_to_NE_I(self):
        self.move_east(0.1218639)
        self.move_north(0.6743167)

    def move_to_NW_Z(self):
        self.move_west(0.0507361)
        self.move_north(0.6743167)

    def move_to_SW_I(self):
        self.move_west(0.0507361)
        self.move_south(0.6471833)

    def move_to_swiccdswg(self):
        self.move_west(0.0717361)
        self.move_south(1.9686033)
        #00.7925361 -> 00.7208 = 0.0717361   -25.2880833 -> -23.3194 = -1.9686033

    def move_to_segccdseb(self):
        self.move_east(0.1218639)
        self.move_south(1.9686833)
        #00.7925361 - 00.9144 = -0.1218639
        #-25.2880833 + 23.3194 = -1.9686833

    def move_to_segccdsec(self):
        self.move_east(0.1154639)
        self.move_south(1.9686833)
        #00.7925361 - 00.908 = -0.1154639
        #-25.2880833 + 23.3194 = = -1.9686833

    def move_to_z_center(self):
        self.move_west(0.0295)
        self.move_north(1.2439)

    def move_to_g_center(self):
        self.move_east(0.1405)
        self.move_north(1.2439)
    
    def calculate_shift(self, x_shift, y_shift, pixel_scale=1):
        # pixel scale is in arcseconds/pixel, x and y shift are in pixels, output is in hours for RA and degrees for Dec
        #convert pixels shifts to radians
        y_shift_rad =np.radians(y_shift * pixel_scale / 3600)
        dec_rad = np.radians(self.dec)
        x_shift_rad = np.radians(x_shift * pixel_scale / 3600)

        dec_numerator = np.sin(dec_rad) + y_shift_rad*np.cos(dec_rad)
        dec_denominator = np.sqrt((np.cos(dec_rad)-y_shift_rad*np.sin(dec_rad))**2
                                  + x_shift_rad**2)
        final_dec = np.degrees(np.arctan2(dec_numerator,dec_denominator))
        degree_ra = np.degrees(np.arctan2(x_shift_rad,(np.cos(dec_rad)-y_shift_rad*np.sin(dec_rad))))
        return degree_ra/15, final_dec-self.dec

class obsplan_entry:
    def __init__(self, line):
        self.is_comment = line.startswith("#")
        if self.is_comment:
            self.raw_line = line.strip()
            return

        elements = line.split("#")
        self.information = ""

        non_commented_elements = elements[0].strip().split()
        assert len(non_commented_elements) >= 7, "Invalid obsplan line: missing information"
        assert non_commented_elements[2] in ["Y", "N","y","n"], "Invalid obsplan line: must have yes/no flag in column 3"
        assert float(non_commented_elements[3]) > 0, "Invalid obsplan line: exposure time must be positive number"
        assert float(non_commented_elements[4]) >= 0, "Invalid obsplan line: cannot have negative time between exposures"
        assert float(non_commented_elements[5]) >=0, "Invalid obsplan line: cannot have negative number of exposures"
        self.coords = coordinates(float(non_commented_elements[0]), float(non_commented_elements[1]))
        self.information = "#" + elements[1].strip()
        self.other_elements = non_commented_elements[2:]

    def get_line(self):
        coord_str = f"{self.coords.ra:.4f} {self.coords.dec:.4f}"
        other_str = " ".join(self.other_elements)
        return f"{coord_str} {other_str} {self.information}"

    def change_comment_to_line(self, comment):
        self.information = "#" + comment

    def add_temporary_comment_to_line(self, comment):
        if self.information == "":
            return self.get_line() + " #" + comment
        else:
            to_return = self.get_line() + comment
            return to_return

x_shift = [-2048*2,-2048,0,2120,2120*2,2120*3,2120*4,2120*5]
y_shift = [-2048*3,-2048,2048,2048*3]
labels= ["NW-A","NW-E","SW-A","SW-E",
        "NW-B","NW-F","SW-B","SW-F",
        "NW-C","NW-G","SW-C","SW-G",
        "NW-D","NW-H","SW-D","SW-H",
        "NE-E","NE-A","SE-A","SE-E",
        "NE-F","NE-B","SE-B","SE-F",
        "NE-G","NE-C","SE-C","SE-G",
        "NE-H","NE-D","SE-D","SE-H",
        ]

def update_obsplan_with_dithers(obsplan_lines):
    updated_lines = []
    for line in obsplan_lines:
        entry = obsplan_entry(line)
        if entry.is_comment:
            updated_lines.append(entry.raw_line)
        else:
            i=0
            for x in x_shift:
                for y in y_shift:
                    ra,dec = entry.coords.calculate_shift(x_shift=x, y_shift=y)
                    #print(f"Calculated shift for x={x}, y={y}: RA shift = {ra} hours, Dec shift = {dec} degrees")
                    entry.coords.add_to_dec(dec)
                    entry.coords.add_to_ra(ra)
                    updated_lines.append(entry.add_temporary_comment_to_line(labels[i]))
                    entry.coords.reset_position()
                    i += 1
    return updated_lines

if __name__ == "__main__":
    obsplan_to_modify = input("Enter the name of the obsplan file to modify: ")
    try :
        with open(obsplan_to_modify, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File {obsplan_to_modify} not found.")

    assert(len(lines) > 0), "Obsplan file is empty."

    obsplan_to_write_to = input("Enter the name you want the updated obsplan to have. If left blank, this will overwrite your current obsplan: ")
    if obsplan_to_write_to == "":
        obsplan_to_write_to = obsplan_to_modify

    with open(obsplan_to_write_to, 'w') as f_out:
        for line in lines:
            lines_to_write = update_obsplan_with_dithers([line])
            for write_line in lines_to_write:
                f_out.write(write_line+"\n")
    print(f"Updated obsplan written to {obsplan_to_write_to}")

