(function() {

  'use strict';

  window.App = Ember.Application.create({
    LOG_TRANSITIONS: true
  });

  App.Router.reopen({
    location: 'auto',
    rootURL: '/hotfixhelper/'
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
    map_to_xml: function() {
      // Example spec
      // <hotfix>
      //   <title>RPE 1.2.3 Hotfix 999</title>
      //   <build>RPE-3.5.2.25-HF5-121</build>
      //   <buildfolder>\\mh-desktop\hotfixbuilds\RPE-3.5.2.25-HF5-121</buildfolder>
      //   <app>10.1.0.181</app>
      //   <web>10.1.0.182</web>
      //   <offline>10.1.0.183</offline>
      //   <issue>
      //     <number>33321</number>
      //     <file>getCustFinTransactionSrch.sql</file>
      //     <file>CaseBusiness.jar</file>
      //     <file>deploy_54321.bat</file>
      //     <summary>Optimized somethign probably</summary>
      //   </issue>
      // </hotfix>
      var model = this.model;
      var xml_doc = document.implementation.createDocument('', '', null);
      var hotfix_tag = xml_doc.createElement('hotfix');

      var append_tag = function(parent, tag_name, text) {
        if (!text) { return }
        var tag = xml_doc.createElement(tag_name);
        tag.appendChild(xml_doc.createTextNode(text));
        parent.appendChild(tag);
      };
      
      append_tag(hotfix_tag, 'title', model.title);
      append_tag(hotfix_tag, 'build', model.build);

      var servers = this.serversByVersion[model.version] || {};
      ['web', 'app', 'offline'].forEach(function(server) {
        append_tag(hotfix_tag, server, servers[server]);
        append_tag(hotfix_tag, server + 'special', model[server + 'special']);
      });

      model.issues.sort(function(a, b) { return a.number.localeCompare(b.number) })
        .forEach(function(issue) {
          var issue_tag = xml_doc.createElement('issue')
          append_tag(issue_tag, 'number', issue.number);
          append_tag(issue_tag, 'summary', issue.summary);
          var files = issue.files || '';
          files.split(/[ \n\t]/).forEach(function(file) {
            append_tag(issue_tag, 'file', file);
          });
          hotfix_tag.appendChild(issue_tag);
      });

      xml_doc.appendChild(hotfix_tag);

      var xml_string = new XMLSerializer().serializeToString(xml_doc);
      return xml_string;
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
      var xml = this.map_to_xml();
      var element = document.createElement('a');
      element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(xml));
      element.setAttribute('download', 'spec.xml');
      element.style.display = 'none';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    },
    onUploadComplete: function() {
      var controller = this;
      return function(e) {
        var xml_string = e.target.result;
        var xmlDoc = $.parseXML(xml_string);
        var $xml = $(xmlDoc);
        controller.load_from_xml($xml);
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