using GLib;

namespace OpenIso.Core.Drawing.Shape {
    public class Line : Object {

        /*
        * = Properties =
        */

        public float Thickness { get; set; default = 1.0f; }

        public string Type { get; set; default = "simple"; }

        public float[] Start { get; set;  default = { 0, 0 }; }

        public float[] End { get; set; default = { 0, 0 }; }

        /* Constructor */
        public Line (float[] _linePositionStart, float[] _linePositionEnd ) {

            this.Start = _linePositionStart;
            this.End = _linePositionStart;

        }
    }
}
