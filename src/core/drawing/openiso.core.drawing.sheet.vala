/* openiso.core.drawing.sheet.vala
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
    public class Sheet : Object {

        /* = Variables = */

        /* = Properties = */
        //** Name of sheet **//
        public string Name { get; set; }

        //** Size of sheet, A3 format by default **//
        // TODO:  Add automatical changing of Width and Height after selecting new size
        // Add list of standard size + Custom for user's size
        public string Size { get; set; default = "A3"; }

        //** Width of sheet **//
        public int Width { get; set; default = 420; }

        //** Height of sheet **//
        public int Height { get; set; default = 297; }

        //** List for storing all shapes of sheet **//
        public Array <GLib.Value?> Shapes { get; set; }

        /* Constructor */
        public Sheet () {

        }

        /* Methods */
        //** Add new shape on sheet - Lines, Circle, Note **//
        public void add_new_shape ( GLib.Variant _new_shape ) {
            this.Shapes.append_val ( _new_shape );
        }
    }
}
