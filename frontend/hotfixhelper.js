(function() {

  'use strict';

  window.App = Ember.Application.create({
    LOG_TRANSITIONS: true
  });

  App.Router.reopen({
    location: 'auto',
    rootURL: '/hotfix/'
  });

  App.IndexRoute = Ember.Route.extend({
    model: function() {
      return Ember.Object.create({
          issues: Ember.A([{}])
        });
    }
  });

  App.IndexController = Ember.Controller.extend({
    init: function() {
      var controller = this;
      Ember.$.getJSON('serversByVersion.json').then(function(servers) {
          controller.set('serversByVersion', servers);
          controller.set('versions', Object.keys(servers));
        });
    },

    serversByVersion: {},
    serialize: function() {
      var model = this.model;
      var spec = {};

      if (model.title) { spec.title = model.title }
      if (model.build) { spec.build = model.build }
      if (model.issues) {
        spec.issues = model.issues.map(function(issue) {
          var result = {};
          if (issue.number) { result.number = issue.number }
          if (issue.summary) { result.summary = issue.summary }
          if (issue.files) { result.files = issue.files.split(/\s/) }
          return result;
        });
      }

      var servers = this.serversByVersion[model.version] || {};
      ['web', 'app', 'offline'].forEach(function(server) {
        if (servers[server]) { spec[server] = servers[server] }
        var special = server + 'special'
        if (model[special]) { spec[special] = model[special]}
      });

      return jsyaml.safeDump(spec);
    },
    deserialize: function(spec) {
      var controller = this;

      var spec = jsyaml.safeLoad(spec);

      this.set('model.title', spec.title);
      this.set('model.build', spec.build);

      ['appspecial', 'webspecial', 'offlinespecial'].forEach(function(tag) {
        controller.set('model.' + tag, spec[tag])
      });

      var issues = Ember.A([]);
      spec.issues.forEach(function(issue) {
        issues.push({
          number: issue.number,
          files: issue.files.join('\n'),
          summary: issue.summary
        });
      });
      controller.set('model.issues', issues);

      // Set Version dropdown by attempting to match app-server IP addr in serversByVersion
      //  to the app-server IP addr in the incoming XML
      for (var version in this.serversByVersion) {
        if (spec['app'] == this.serversByVersion[version]['app']) {
          controller.set('model.version', version);
          break;
        }
      }
    },
    load_from_xml: function(xml) {
      var controller = this;
      var issues_list = Ember.A([]);

      this.set('model.title', xml.find('title').text());
      this.set('model.build', xml.find('build').text());
      ['appspecial', 'webspecial', 'offlinespecial'].forEach(function(tag) {
        controller.set('model.' + tag, xml.find(tag).text());
      });
      $.each(xml.find('issue'), function(index, issue_tag) {
        var issue = {},
          $issue = $(issue_tag);
        issue.number = $issue.find('number').text();
        var files_list = $.map($issue.find('file'), function(f) { return $(f).text() });
        issue.files = files_list.join('\n');
        issue.summary = $issue.find('summary').text();
        issues_list.push(issue);
      });
      // Set Version dropdown by attempting to match app-server IP addr in serversByVersion
      //  to the app-server IP addr in the incoming XML
      for (var version in this.serversByVersion) {
        if (xml.find('app').text() == this.serversByVersion[version]['app']) {
          this.set('model.version', version);
        }
      }
      this.set('model.issues', issues_list);
    },
    download: function() {
      var serialized = this.serialize();
      var element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(serialized));
      element.setAttribute('download', 'spec.yaml');
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    },
    onUploadComplete: function() {
      var controller = this;
      return function(e) {
        var upload_string = e.target.result;
        controller.deserialize(upload_string);
      }
    },
    upload: function() {
      var element = document.createElement('input');
      var controller = this;
      element.setAttribute('type', 'file');
      element.style.display = 'none';
      document.body.appendChild(element);
      element.addEventListener('change', function(event) {
          var file = event.target.files[0];
          var reader = new FileReader();
          reader.onload = controller.onUploadComplete();
          reader.readAsText(file);
        }, false);
      element.click();
      document.body.removeChild(element);
    },
    actions: {
      addIssue: function() {
        this.model.issues.pushObject({});
      },
      deleteIssue: function(issue) {
        this.model.issues.removeObject(issue);
      },
      download: function() {
        this.download();
      },
      upload: function() {
        this.upload();
      }
    }
  });

  App.IssueItemComponent = Ember.Component.extend({
    actions: {
      delete: function() {
        this.sendAction("delete-action", this.get('issue'));
      }
    },
    trackplusurl: function() {
      return "https://track.rsimail.com/track/printItem.action?key=" + this.get('issue.number');
    }.property('issue.number')
  });

})();