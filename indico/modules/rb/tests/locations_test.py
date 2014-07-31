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

from dictdiffer import diff
from sqlalchemy import exists

from indico.core.db import db
from indico.modules.rb.models.aspects import Aspect
from indico.modules.rb.models.locations import Location
from indico.modules.rb.models.rooms import Room
from indico.modules.rb.models.utils import clone, getDefaultValue
from indico.tests.db.data import *
from indico.tests.db.environment import DBTest


class TestLocation(DBTest):

    def iterLocations(self):
        for l in LOCATIONS:
            loc = Location.getLocationByName(l['name'])
            yield l, loc
            db.session.add(loc)
        transaction.commit()

    def compare_dict_and_object(self, d, o):
        for k, v in d.items():
            assert_equal(v, getattr(o, k))

#TESTS_RUNNING

    def testGetLocator(self):
        for l, loc in self.iterLocations():
            assert_equal(loc.getLocator()['locationId'], l['name'])

    def testGetSupportEmails(self):
        for l, loc in self.iterLocations():
            if 'support_emails' in l:
                assert_equal(loc.getSupportEmails(to_list=False), l['support_emails'])
                assert_equal(loc.getSupportEmails(), l['support_emails'].split(','))

    def testSetSupportEmails(self):
        for i, (l, loc) in enumerate(self.iterLocations()):
            loc.setSupportEmails(['a{}@example.com'.format(i), 'b{}@example.com'.format(i)])

        for i, (l, loc) in enumerate(self.iterLocations()):
            assert_equal(loc.support_emails, 'a{i}@example.com,b{i}@example.com'.format(i=i))

    def testAddSupportEmails(self):
        for l, loc in self.iterLocations():
            loc.addSupportEmails('testing@cern.ch')

        for _, loc in self.iterLocations():
            assert_in('testing@cern.ch', loc.getSupportEmails())

    def testAddSupportEmailsExisting(self):
        emails = []
        for l, loc in self.iterLocations():
            emails.append(loc.getSupportEmails())
            loc.addSupportEmails(*emails[-1][:])

        for (_, loc), e in zip(self.iterLocations(), emails):
            assert_equal(sorted(loc.getSupportEmails()), sorted(e))

    def testDeleteSupportEmails(self):
        test_email = 'testing-experimental@cern.ch'
        for l, loc in self.iterLocations():
            loc.addSupportEmails(test_email)

        for _, loc in self.iterLocations():
            assert_in(test_email, loc.getSupportEmails())
            loc.deleteSupportEmails(test_email)

        for _, loc in self.iterLocations():
            assert_not_in(test_email, loc.getSupportEmails())

    def testGetAspects(self):
        for l, loc in self.iterLocations():
            for aspect_dict, aspect in zip(l.get('aspects', []), loc.getAspects()):
                self.compare_dict_and_object(aspect_dict, aspect)

    def testGetDefaultAspect(self):
        for l, loc in self.iterLocations():
            if 'default_aspect_id' in l:
                self.compare_dict_and_object(ASPECTS[l['default_aspect_id']], loc.default_aspect)
            else:
                assert_is(loc.default_aspect, None)

    def testSetDefaultAspect(self):
        test_aspect_name = 'testing-aspect'
        for l, loc in self.iterLocations():
            if loc.default_aspect:
                test_aspect = clone(Aspect, loc.default_aspect)
                test_aspect.name = l['name'] + test_aspect_name
                loc.aspects.append(test_aspect)
                loc.setDefaultAspect(test_aspect)

        for _, loc in self.iterLocations():
            if loc.default_aspect:
                assert_equal(loc.default_aspect.name, (loc.name + test_aspect_name))

    def testIsMapAvailable(self):
        for l, loc in self.iterLocations():
            assert_equal(loc.isMapAvailable(), ('aspects' in l))

    def testGetDefaultLocation(self):
        for l, loc in self.iterLocations():
            if 'is_default' in l:
                assert_equal(loc, Location.getDefaultLocation())

    def testGetLocationByName(self):
        for l, loc in self.iterLocations():
            assert_equal(l['name'], loc.name)

    def test_get_buildings(self):
        for l, loc in self.iterLocations():
            buildings = {}
            for r in l.get('rooms', []):
                k = r.get('building')
                if k in buildings:
                    buildings[k]['rooms'].append(r['name'])
                    buildings[k]['has_coordinates'] = (buildings[k]['has_coordinates'] or
                                                       bool(r.get('latitude', False) and r.get('longitude', False)))
                else:
                    buildings[k] = {
                        'number': k,
                        'title': 'Building {}'.format(k),
                        'rooms': [r['name']],
                        'has_coordinates': bool(r.get('latitude', False) and r.get('longitude', False))
                    }
            for b in loc.get_buildings():
                k = b['number']
                assert_in(k, buildings)
                for r in b['rooms']:
                    assert_in(r['name'], buildings[k]['rooms'])

#TESTS_TO_BE_IMPLEMENTED

    def test_set_default(self):
        pass
