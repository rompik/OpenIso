/* openiso.core.piping.pipe.vala
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
using OpenIso.Core;

namespace OpenIso.Core.Piping {
    public class Pipe : Object {

        /* = Variables = */
        private Array <Piping.Component> _property_components = new Array <Piping.Component> ();

        /* = Properties = */
        //** Name of pipe **//
        public string Name { get; set; }

        //** Name of spec of pipe **//
        public string Spec { get; set; }

        //** Pipe Nominal Pressure Rating **//
        public double PressureRating { get; set; }

        //** Pipe Line Type **//
        public string LineType { get; set; }

        //** Pipe Insulation Spec **//
        public string Insulation { get; set; }

        //** Pipe Tracing Spec **//
        public string Tracing { get; set; }

        //** Pipe Painting Spec **//
        public string Painting { get; set; }

        //** Pipe Temperature **//
        public double Temperature { get; set; }

        /* List of components */
        public Array <Piping.Component> Components {
            get { return _property_components;}
            set { _property_components = value;}
        }

        /* List of Revisions */
        public Array <Revisions.Revision> Revisions { get; set; }

        /* = Constructor = */
        public Pipe () {

        }

        /* = Methods = */
        /* Add new component */
        public void AddComponent ( Piping.Component _component_new) {
           this.Components.append_val ( _component_new );
        }
    }
}
