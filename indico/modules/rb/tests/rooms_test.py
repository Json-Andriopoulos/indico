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


from pprint import pprint
import transaction

from nose.tools import assert_equal, assert_not_equal, assert_is, assert_is_not,\
    assert_in, assert_not_in, assert_true, assert_false

from indico.core.db import db
from indico.modules.rb.models.rooms import Room
from indico.tests.db.data import ROOMS, LOCATIONS
from indico.tests.db.environment import DBTest
from indico.tests.db.util import diff


class TestRoom(DBTest):
    """
    Testing the most important functions of the Room class from
    the room booking models.
    """

    def iterRooms(self):
        for r in ROOMS:
            room = Room.find_first(Room.name == r['name'])
            yield r, room
            db.session.add(room)
        transaction.commit()

    def test_is_auto_confirm(self):
        for r, room in self.iterRooms():
            needs_confirmation = 'reservations_need_confirmation' in r and r['reservations_need_confirmation']
            assert_not_equal(room.is_auto_confirm, needs_confirmation)

    def test_booking_url(self):
        for r, room in self.iterRooms():
            if room.id is None:
                assert_is(room.booking_url, None)
            else:
                assert_is_not(room.booking_url, None)

    def test_details_url(self):
        for r, room in self.iterRooms():
            if room.id is None:
                assert_is(room.details_url, None)
            else:
                assert_is_not(room.details_url, None)

    def test_full_name(self):
        for r, room in self.iterRooms():
            if room.has_special_name:
                assert_in(r['name'], room.full_name)
            assert_in(room.generate_name(), room.full_name)

    def test_has_booking_groups(self):
        for r, room in self.iterRooms():
            assert_equal(room.has_booking_groups,
                         'attributes' in r and
                         any(attr['name'] == 'allowed-booking-group' for attr in r['attributes']))

    def test_has_projector(self):
        for r, room in self.iterRooms():
            assert_equal('available_equipment' in r and 'Computer Projector' in r['available_equipment'],
                         room.has_projector)

    def test_has_special_name(self):
        for r, room in self.iterRooms():
            assert_equal(room.has_special_name, 'name' in r and r['name'] is not None)

    def test_has_webcast_recording(self):
        for r, room in self.iterRooms():
            assert_equal('available_equipment' in r and 'Webcast/Recording' in r['available_equipment'],
                         room.has_webcast_recording)

    def test_is_public(self):
        for r, room in self.iterRooms():
            assert_equal(room.is_public, room.is_reservable and (not room.has_booking_groups))

    def test_kind(self):
        for r, room in self.iterRooms():
            if room.is_public:
                if room.is_auto_confirm:
                    assert_equal(room.kind, 'basicRoom')
                else:
                    assert_equal(room.kind, 'moderatedRoom')
            else:
                assert_equal(room.kind, 'privateRoom')

    def test_location_name(self):
        for r, room in self.iterRooms():
            found_in_data = False
            for loc in LOCATIONS:
                if room.location_name == loc['name']:
                    location_rooms = []
                    for loc_room in loc['rooms']:
                        location_rooms.append(loc_room['name'])
                    assert_in(room.name, location_rooms)
                    found_in_data = True
            assert_true(found_in_data)

    def test_marker_description(self):
        for r, room in self.iterRooms():
            description = room.marker_description
            if room.capacity:
                assert_in(str(room.capacity), description)
            if room.is_public:
                assert_in('public', description)
            else:
                assert_in('private', description)
            if room.is_auto_confirm:
                assert_in('auto-confirmation', description)
            else:
                assert_in('needs confirmation', description)

    def test_large_photo_url(self):
        for r, room in self.iterRooms():
            if room.id is None:
                assert_is(room.large_photo_url, None)
            else:
                assert_is_not(room.large_photo_url, None)

    def test_small_photo_url(self):
        for r, room in self.iterRooms():
            if room.id is None:
                assert_is(room.small_photo_url, None)
            else:
                assert_is_not(room.small_photo_url, None)

    def test_has_photo(self):
        for r, room in self.iterRooms():
            if room.photo_id is None:
                assert_false(room.has_photo)
            else:
                assert_true(room.has_photo)

    def test_has_equipment(self):
        for r, room in self.iterRooms():
            if 'available_equipment' in r:
                for equip in r['available_equipment']:
                    assert_true(room.has_equipment(equip))
            assert_false(room.has_equipment('This equipment does not exist'))

    def test_find_available_video_conference(self):
        pass

    def test_get_attribute_by_name(self):
        for r, room in self.iterRooms():
            if 'attributes' in r:
                for attr in r['attributes']:
                    assert_is_not(room.get_attribute_by_name(attr['name']), None)
            assert_is(room.get_attribute_by_name('This attribute does not exist'), None)

    def test_has_attribute(self):
        for r, room in self.iterRooms():
            if 'attributes' in r:
                for attr in r['attributes']:
                    assert_true(room.has_attribute(attr['name']))
            assert_false(room.has_attribute('This attribute does not exist'))

    def testGetLocator(self):
        for r, room in self.iterRooms():
            l = room.getLocator()
            assert_equal(l['roomLocation'], room.location.name)
            assert_equal(l['roomID'], room.id)

    def test_generate_name(self):
        for r, room in self.iterRooms():
            if room.building:
                assert_in(r['building'], room.generate_name())
            if room.floor:
                assert_in(r['floor'], room.generate_name())
            if room.number:
                assert_in(r['number'], room.generate_name())

    def test_full_name(self):
        for r, room in self.iterRooms():
            assert_in(room.name, room.full_name)
            assert_in(room.generate_name(), room.full_name)

    def test_update_name(self):
        for r, room in self.iterRooms():
            if room.building and room.floor and room.number:
                room.name = ''
                room.update_name()
                assert_true(len(room.name) > 0)

    def test_find_all(self):
        all_rooms = Room.find_all()

        lista = []
        #we get the concatenation of location.name and full name because
        #these values are used for sorting in the find_all method.
        for r, room in self.iterRooms():
            lista.append(room.location.name + room.full_name)

        lista = sorted(lista)
        assert_equal(len(all_rooms), len(lista))

        for i in range(len(all_rooms)):
            assert_equal(all_rooms[i].location.name + all_rooms[i].full_name, lista[i])

    def test_find_with_attribute(self):
        for r, room in self.iterRooms():
            for attr in r['attributes']:
                rooms_with_attr = []
                for room_with_attr in Room.find_with_attribute(attr['name']):
                    rooms_with_attr.append(room_with_attr[0])
                assert_in(room, rooms_with_attr)

    def getRoomsWithData(*args, **kwargs):
        pass

    def test_max_capacity(self):
        max_capacity = 0
        for r, room in self.iterRooms():
            if 'capacity' in r:
                max_capacity = r['capacity'] if r['capacity'] > max_capacity else max_capacity
        assert_equal(max_capacity, Room.max_capacity)

    def filter_available(start_dt, end_dt, repetition, include_pre_bookings=True, include_pending_blockings=True):
        pass

    def getRoomsForRoomList(form, avatar):
        pass

    def has_live_reservations(self):
        for r, room in self.iterRooms():
            def is_live(resv):
                #Live reservations: Happening now or future reservations.
                return resv['start_date'] >= datetime.datetime.utcnow() or \
                    resv['end_date'] >= datetime.datetime.utcnow()
            c = len(filter(is_live, r.get('reservations', []))) > 0
            assert_equal(c, room.doesHaveLiveReservations())

    def isAvatarResponsibleForRooms(avatar):
        pass

    def removeEquipment(self, equipment_name):
        pass

    def get_blocked_rooms(self, *dates, **kwargs):
        pass

    def test_get_attribute_value(self):
        pass

    def _can_be_booked(self, avatar, prebook=False, ignore_admin=False):
        pass

    def test_can_be_booked(self):
        pass

    def can_be_overriden(self, avatar):
        pass

    def can_be_prebooked(self, avatar, ignore_admin=False):
        pass

    def can_be_modified(self, accessWrapper):
        pass

    def can_be_deleted(self, accessWrapper):
        pass

    def test_is_owned_by(self):
        pass

    def check_advance_days(self, end_date, user=None, quiet=False):
        pass

    def check_bookable_times(self, start_time, end_time, user=None, quiet=False):
        pass
