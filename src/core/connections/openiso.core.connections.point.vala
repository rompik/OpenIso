/* openiso.core.connections.point.vala
 *
 * Copyright (C) 2016 Rompik <rompik@mail.ru>
 *
 * This file is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation; either version 3 of the
 * License, or (at your option) any later version.
 *
 * This file is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * class OpenIso.Core.Connections.Point
 * Class for creating Connection Point - Arrive or Leave
 */


using GLib;

namespace OpenIso.Core.Connections {
    public class Point : Object {

        /* Variables */


        /* = Properties = */
        /* Type of connection */
        /* TODO: Add condition to check correct type
         * 1 - ARRIVE
         * 2 - LEAVE
         * 3 - SUPPORT
         * 4 - RPAD
         * 5 - TAPPING
        */
        public string Type { get; set; default = "ARRIVE"; }

        //*Number of Point*//
        public int Number { get; set; }

        //* Bore of connection *//
        public double Bore { get; set; default = 0;}

        //* Reference to connected component *//
        public string Ref { get; set; }

        //* 3D coordinates of connection - East/West *//
        public double PosEast { get; set; default = 0;}

        //* 3D coordinates of connection - North/South *//
        public double PosNorth { get; set; default = 0;}

        //* 3D coordinates of connection - Elevation +/- *//
        public double PosElev { get; set; default = 0;}

        /* Constructor */
        public Point () {
            //this.Number = _number;
        }

        /* = Methods = */

    }
}
