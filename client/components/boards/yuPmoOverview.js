import { ReactiveCache } from '/imports/reactiveCache';
import { Meteor } from 'meteor/meteor';

Template.yuPmoOverview.helpers({
  yuProjectCount() {
    if (!Meteor.userId()) return 0;
    const boards = ReactiveCache.getBoards(
      {
        archived: false,
        type: 'board',
        'members.userId': Meteor.userId(),
      },
      {},
    );
    return Array.isArray(boards) ? boards.length : 0;
  },
});
