/* openiso.core.mto.material.vala
 *
 * Copyright (C) 2016 Rompik <rompik@mail.ru>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

namespace OpenIso.Core.MTO {
    public class Material : Object {

        //* Material Code *//
        //* TODO: Add changing description when setup new code *//
        public string Code { get; set; default = "XXXXXXXX"; }

        //* Material Description *//
        public string Description { get; set; default = "Default Description"; }

        /* Constructor */
        //* Add method to fill description by getting code of material*//
        public Material () {

        }

    }
}
