/* openiso.core.drawing.note.text.vala
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

namespace OpenIso.Core.Drawing.Note {
    public class Text : Object {

        /*
         * = Properties =
         */

        /*
         * == Text of Atext ==
         */
        public string Text { get; set; }


        /*
        * == Text Size of note ==
        */
        public int Size { get; set; default = 10; }


        /*
         * == Text Font of note ==
         */
        public string Font { get; set; default = "GOST"; }

        /*
         * == Text Font Bold ==
         */
        public bool Bold { get; set; default = false; }

        /*
         * == Text Font Italic ==
         */
        public bool Italic { get; set; default = false; }

        /*
         * == Position of note ==
         */

        public float[] Position { get; set; default = {0, 0}; }

        /*
         * == Horisontal align of note ==
         */

        public string AlignHorizontal { get; set; default = "left"; }

        /*
         * == Vertical align of note ==
         */

        public string AlignVertical { get; set; default = "bottom"; }


        /* Constructor */
        public Text () {

        }
    }
}
