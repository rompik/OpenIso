/**
 * class OpenIso.Core.Connections.Point
 * Class for creating Connection Point - Arrive or Leave
 */


using GLib;

namespace OpenIso.Core.Connections {
    public class Point : Object {

        /* Variables */


        /* = Properties = */
        /* Type of connection */
        /* TODO: Add condition to check correct type
         * 1 - ARRIVE
         * 2 - LEAVE
         * 3 - SUPPORT
         * 4 - RPAD
         * 5 - TAPPING
        */
        public string Type { get; set; default = "ARRIVE"; }

        //*Number of Point*//
        public int Number { get; set; }

        //* Bore of connection *//
        public double Bore { get; set; }

        //* Reference to connected component *//
        public string Ref { get; set; }

        //* 3D coordinates of connection *//
        public double[] Position { get; set; }

        /* Constructor */
        public Point (int _point_number) {

            this.Number = _point_number;

        }

        /* = Methods = */

    }
}
