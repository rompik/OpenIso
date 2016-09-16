/* openiso.core.drawing.skey.vala
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

using GLib;

namespace OpenIso.Core.Drawing {
    public class Skey : Object {

        /*
         * = Properties =
         */

        /*
         * == Name of skey ==
         * TODO: Add random value for name
        */
        public string Name { get; set; default = "AAAAAAAA"; }

        /*
         * == Description of Skey ==
         */
        public string Description { get; set; default = "Default description of new Skey"; }

        /*
         * == Shapes of Skey
         */
        public Array <GLib.Value?> Shapes { get; set; }

        /* Constructor */
        public Skey () {

        }

        //** Methods **//
        // Adding new shape for skey
        public void add_shape (GLib.Variant _new_shape) {

            this.Shapes.append_val ( _new_shape );

        }
    }
}
