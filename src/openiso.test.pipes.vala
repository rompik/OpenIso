/* openiso.test.pipes.vala
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

using OpenIso.Core;

namespace OpenIso {
    public class Test {

        /* Array of test pipes with components */
        private Array <Piping.Pipe> property_pipes = new Array <Piping.Pipe> ();

        public Test () {

            //* Add Pipe Block *//
            for (int i = 0; i < 5; i++) {
                property_pipes.append_val (new Piping.Pipe ());
                property_pipes.index(i).Name = "000-XXX-000/000-150-XX-00000-XXXXXX-" + i.to_string();
                property_pipes.index(i).Spec = "01SPECS";
                property_pipes.index(i).PressureRating = 150;
                property_pipes.index(i).LineType = "OIL";
                property_pipes.index(i).Insulation = "INS";
                property_pipes.index(i).Tracing = "TRACED";
                property_pipes.index(i).Temperature = 50;

                for (int j = 0; j < 10; j++) {
                    property_pipes.index(i).AddComponent (new Piping.Component ());
                    property_pipes.index(i).Components.index(j).Name = "GASKET_" + j.to_string();
                    property_pipes.index(i).Components.index(j).Subtype = "GASK";

                    //property_pipes.index(i).AddComponent (new Piping.Component ());
                    //property_pipes.index(i).Components.index(j).Name = "FLANGE_" + j.to_string();
                    //property_pipes.index(i).Components.index(j).Subtype = "FLAN";

                    //property_pipes.index(i).AddComponent (new Piping.Component ());
                    //property_pipes.index(i).Components.index(j).Name = "FLANGE_" + j.to_string();
                    //property_pipes.index(i).Components.index(j).Subtype = "FLAN";
                }
            }

        }

        public Array <Piping.Pipe> Pipes {
            get { return this.property_pipes; }
            set { this.property_pipes = value;}
        }

    }
}
