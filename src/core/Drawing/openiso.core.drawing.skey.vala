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
