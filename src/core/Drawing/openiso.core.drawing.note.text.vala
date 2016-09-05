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
