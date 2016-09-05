using GLib;
using OpenIso.Core;

namespace OpenIso.Core.Piping {
    public class Component : Object {


        /* = Variables = */
		private double _length = 0;

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
        public string Weight { get; set; }

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
        public HashTable <int, Connections.Point> Connections { get; set; }

        /* = Constructor = */
        public Component () {

        }

        /* = Methods = */
        /* Add new connection point */
        public void AddConnection ( Connections.Point _component_point_new ) {
            //this.Connections.insert ( _component_point_new.Number, _component_point_new );
        }
    }
}
