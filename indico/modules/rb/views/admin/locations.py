# -*- coding: utf-8 -*-
##
##
## This file is part of Indico.
## Copyright (C) 2002 - 2013 European Organization for Nuclear Research (CERN).
##
## Indico is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.
##
## Indico is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Indico;if not, see <http://www.gnu.org/licenses/>.

from MaKaC.webinterface.wcomponents import WTemplated

from . import WPRoomBookingPluginAdminBase
from indico.modules.rb.models.room_attributes import RoomAttribute
from indico.modules.rb.models.locations import Location
from indico.util.string import natural_sort_key


class WPRoomBookingAdmin(WPRoomBookingPluginAdminBase):
    def __init__(self, rh):
        self._rh = rh
        WPRoomBookingPluginAdminBase.__init__(self, rh)

    def _setActiveTab(self):
        self._subTabConfig.setActive()

    def _getTabContent(self, params):
        return WRoomBookingAdmin(self._rh).getHTML(params)


class WRoomBookingAdmin(WTemplated):
    def __init__(self, rh):
        self._rh = rh

    def getVars(self):
        wvars = WTemplated.getVars(self)
        wvars['locations'] = Location.find_all()
        defaultLocation = Location.getDefaultLocation()
        wvars['defaultLocationName'] = defaultLocation.name if defaultLocation else ''
        return wvars


class WPRoomBookingAdminLocation(WPRoomBookingPluginAdminBase):
    def __init__(self, rh, location, actionSucceeded=False):
        self._rh = rh
        self._location = location
        self._actionSucceeded = actionSucceeded
        WPRoomBookingPluginAdminBase.__init__(self, rh)

    def _setActiveTab(self):
        self._subTabConfig.setActive()

    def _getTabContent(self, params):
        wc = WRoomBookingAdminLocation(self._rh, self._location)
        params['actionSucceeded'] = self._actionSucceeded
        return wc.getHTML(params)


class WRoomBookingAdminLocation(WTemplated):
    def __init__(self, rh, location):
        self._rh = rh
        self._location = location

    def getVars(self):
        wvars = WTemplated.getVars(self)
        wvars['location'] = self._location
        wvars['possibleEquipments'] = self._location.getEquipmentNames()
        wvars['attributes'] = self._location.attributes.all()

        # TODO: rest
        wvars['keys'] = RoomAttribute

        # Rooms
        wvars['rooms'] = sorted(self._location.rooms, key=lambda r: natural_sort_key(r.full_name))

        rh = self._rh
        wvars['withKPI'] = rh._withKPI
        if rh._withKPI:
            wvars['kpiAverageOccupation'] = '{0:.02f}%'.format(rh._kpiAverageOccupation * 100)

            wvars['kpiTotalRooms'] = rh._kpiTotalRooms
            wvars['kpiActiveRooms'] = rh._kpiActiveRooms
            wvars['kpiReservableRooms'] = rh._kpiReservableRooms

            wvars['kpiReservableCapacity'] = rh._kpiReservableCapacity
            wvars['kpiReservableSurface'] = rh._kpiReservableSurface

            # Bookings
            wvars['kbiTotalBookings'] = rh._totalBookings

            # Next 9 KPIs
            wvars['stats'] = rh._booking_stats

        return wvars
