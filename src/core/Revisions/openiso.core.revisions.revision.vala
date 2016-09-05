namespace OpenIso.Core.Revisions {
    public class Revision : Object {

        //*String for Revision number - 1, 2, 3 or A, B, C*//
        private string _number = null;

        /* Constructor */
        public Revision (string _RevNumber) {
            _number = _RevNumber;
        }
    }
}
