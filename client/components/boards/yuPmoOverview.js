import { ReactiveCache } from '/imports/reactiveCache';
import { Meteor } from 'meteor/meteor';

function yuVisibleProjects() {
  if (!Meteor.userId()) return [];
  const boards = ReactiveCache.getBoards(
    {
      archived: false,
      type: 'board',
      'members.userId': Meteor.userId(),
    },
    {},
  );
  if (!Array.isArray(boards)) return [];
  return boards
    .slice()
    .sort((a, b) => {
      const aTime = a.modifiedAt || a.createdAt || 0;
      const bTime = b.modifiedAt || b.createdAt || 0;
      return new Date(bTime).getTime() - new Date(aTime).getTime();
    })
    .slice(0, 8);
}

Template.yuPmoOverview.helpers({
  yuProjectCount() {
    return yuVisibleProjects().length;
  },
  yuProjects() {
    return yuVisibleProjects();
  },
});
