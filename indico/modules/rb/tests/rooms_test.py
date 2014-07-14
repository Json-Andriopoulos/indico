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

from datetime import datetime
from pprint import pprint

import transaction

from indico.core.db import db
from indico.modules.rb.models.room_attributes import RoomAttribute
from indico.modules.rb.models.room_equipments import RoomEquipment
from indico.modules.rb.models.rooms import Room
from indico.tests.db.data import *
from indico.tests.db.environment import DBTest
from indico.tests.db.util import diff


class TestRoom(DBTest):
    """
    Testing the most important functions of the Room class from
    the room booking models.
    """

    def iterRooms(self):
        for r in ROOMS:
            room = Room.getRoomByName(r['name'])
            yield r, room
            db.session.add(room)
        transaction.commit()

#*****************************************CHECKED_AND_RUNNING**********************************************************

    def testGetLocator(self):
        for r, room in self.iterRooms():
            l = room.getLocator()
            assert l['roomLocation'] == room.location.name
            assert l['roomID'] == room.id

    def testGetRooms(self):
        for r, room in self.iterRooms():
            assert diff(r, room)

    def testDoesHaveLiveReservations(self):
        for r, room in self.iterRooms():
            def is_live(resv):
                #Live reservations: Happening now or future reservations.
                return resv['start_date'] >= datetime.utcnow() or resv['end_date'] >= datetime.utcnow()
            c = len(filter(is_live, r.get('reservations', []))) > 0
            assert c == room.doesHaveLiveReservations()

    def testGetCollisions(self):
        for p in NO_RESERVATION_PERIODS:
            for r, room in self.iterRooms():
                assert len(room.getCollisions(p[0], p[1])) == 0
        for p in RESERVATION_PERIODS:
            assert any(len(room.getCollisions(p[0], p[1])) > 0 for r, room in self.iterRooms())

    def testGetReservationStats(self):
        for r, room in self.iterRooms():
            reservations_num = 0
            for res in room.getReservationStats():
                reservations_num += room.getReservationStats()[res]
            assert reservations_num == len(r.get('reservations', []))

    def testGetTotalBookedTime(self):
        for r, room in self.iterRooms():
            if len(r.get('reservations', [])) > 0:
                assert any(room.getTotalBookedTime(period[0], period[1]) > 0 for period in RESERVATION_PERIODS)
            else:
                assert all(room.getTotalBookedTime(period[0], period[1]) == 0 for period in NO_RESERVATION_PERIODS)

    def testGetVerboseEquipment(self):
        e1 = RoomEquipment(name='eq1', location_id=1)
        e2 = RoomEquipment(name='eq2', location_id=1)

        room = Room.get(5)
        room.equipments.extend([e1, e2])
        db.session.add(room)
        transaction.commit()

        equipment_added = unicode('eq1, eq2')
        assert equipment_added == Room.get(5).getVerboseEquipment()

#******************************************************NON_RUNNING*****************************************************

    def testGetTotalBookableTime(self):
        for r, room in self.iterRooms():
            print room.getTotalBookableTime(RESERVATION_PERIODS[0][0], RESERVATION_PERIODS[0][1])

    def testGetAverageOccupation(self):
        for r, room in self.iterRooms():
            pprint(room.getAverageOccupation(datetime(2012, 1, 1), datetime(2015, 1, 1)))
