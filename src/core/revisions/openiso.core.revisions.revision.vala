/* openiso.core.revisions.revision.vala
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
