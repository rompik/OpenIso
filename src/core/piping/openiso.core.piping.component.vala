/* openiso.core.piping.component.vala
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
    public class Component : Object {


        /* = Variables = */
		private double _length = 0;
        private Array <Connections.Point?> _connections = new Array <Connections.Point?> ();

        /* = Properties = */
        //* Name of component *//
        public string Name { get; set; }

        //* Type of Component *//
        public string Type { get; set; }

		//* Start position of component *//
		public double[] PosStart { get; set; }

		//* End position of component *//
		public double[] PosEnd { get; set; }

        //* Subtype of Component *//
        public string Subtype { get; set; }

        //* Skey of Component *//
        public string Skey { get; set; }

        //* Insulation specification *//
        public bool Insulation { get; set; }

        //* Tracing specification *//
        public bool Tracing { get; set; }

        //* Weight of component *//
        public double Weight { get; set; }

        //* Material of component *//
        public MTO.Material Material { get; set; }

        //* Length of component - mainly for tube *//
        public double Length {
			get { return _length; }
			set { _length = value; }
		}

        //* Component has to be shop or done on the site *//
        /* TODO: Add 2 possible values
         * 1) ERECTION ITEM - FALSE;
         * 2) FABRICATION ITEM - TRUE;
         */
        public bool Shop { get; set; }

        //* Conenction Points *//
        public Array <Connections.Point> Connections {
            get {return _connections; }
            set { _connections = value; }
        }

        /* = Constructor = */
        public Component () {

        }

        /* = Methods = */
        /* Add new connection point */
        public void AddConnection ( Connections.Point? _component_point ) {
            // * TODO: Add HashTable to prevent duplication of points numbers *//
            _connections.append_val ( _component_point );
        }
    }
}
