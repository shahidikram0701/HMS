console.clear();

var myApp = angular.module('myApp', []);

myApp.controller('MedicalProfileCtrl', function($scope){
	$scope.init = function(name, username, email, phone, dob, gender, height, weight, bloodType, organDonor, ailment1, ailment2, ailment3, ailment4, ailment5, ailment6, ailment7, ailment8, ailment9, ailment10, ailment11, ailment12, medical_conditions) {
		//console.log(arguments);
		$scope.dataModel = {
			personalInfo: {
				'name': name,
				'username': username,
				'email': email,
				'phone': phone,
				'dob': dob,
				'gender': gender,
				'height': height,
				'weight': weight,
				'bloodType': bloodType,
				'organDonor': organDonor 
			},
			medicalQuest: {
				'ailment1': ailment1,
				'ailment2': ailment2,
				'ailment3': ailment3,
				'ailment4': ailment4,
				'ailment5': ailment5,
				'ailment6': ailment6,
				'ailment7': ailment7,
				'ailment8': ailment8,
				'ailment9': ailment9,
				'ailment10': ailment10,
				'ailment11': ailment11,
				'ailment12': ailment12,            
			},
			medicalConditions: medical_conditions
		};
	}
});

myApp.directive('medicalPersonalInfo', function(){
	return {
		scope: {
			model: "=",
			id: "="
		},
		link: function(scope){
			var labels = {
				name: "Name",
				username: "Username",
				email: "Email ID",
				phone: "Phone Number",
				dob: "Date of Birth",
				gender: "Gender",
				height: "Height(cms)",
				weight: "Weight(kgs)",
				bloodType: "Blood Type",
				organDonor: "Organ Donor"
			};
			
			// models
			angular.extend(scope, {
				labels: labels,
				viewModel: scope.model,
				editModel: {}
			});
			
			// automatically update viewModel if model change
			scope.$watch('model', function(newVal, oldVal){
				scope.viewModel = scope.model;
			});
			
			// methods
			angular.extend(scope, {
				showEditModalFn: function(viewModel, editModalId){
					scope.editModel = viewModel ? angular.copy(viewModel) : {};
					$(editModalId).modal('toggle');
				},
				saveEditFn: function(editModalId){
					// pass data back
					scope.model = angular.copy(scope.editModel);
					// ajax call to save stuff into Database
					// console.log(scope.editModel);
					var data = scope.editModel;
					$.ajax({
						type: "GET",
						url: "/update_personal_info?name=" + data["name"] + "&email=" + data["email"] + "&phone=" + data["phone"] + "&dob=" + data["dob"] + "&gender=" + data["gender"] + "&height=" + data["height"] + "&weight=" + data["weight"] + "&bloodType=" + data["bloodType"] + "&organDonor=" + data["organDonor"] 
					}).done(function(o) {
						swal({
							title: "Success",
							text: o,
							type: "success"
							}, function(){
							  console.log("success");    
						}); 
					});
					// clean UI
					$(editModalId).modal('toggle');
				}
			});
		},
		template: $("#medicalPersonalInfoTemplate").html(),
		replace: true
	};
});
myApp.directive('medicalConditions', function(){
	return {
		scope: {
			model: "=",
			id: "="
		},
		link: function(scope){
			var labels = {
				mode: "Add",
				condition: "Condition",
				note: "Note"
			};
			
			// models
			angular.extend(scope, {
				labels: labels,
				viewModel: scope.model,
				editModel: {}
			});
			
			// methods
			angular.extend(scope, {
				showEditModalFn: function(viewModel, index, editModalId){
					labels.mode = viewModel ? "Edit" : labels.mode;
					scope.editModel = viewModel ? angular.copy(viewModel) : {};
					scope.editModel.index = index;
					$(editModalId).modal('toggle');
				},
				saveEditFn: function(editModalId){
					// pass data back
					if (scope.editModel.index != null){
						scope.model[scope.editModel.index] = angular.copy(scope.editModel);
					} else {
						scope.model.push(angular.copy(scope.editModel));
					}
					var str = jQuery.param( scope.editModel );
					// console.log(str)
					// console.log(scope.editModel);
					// console.log(scope.model);

					$.ajax({
						type: "GET",
						url: "/update_medical_conditions?" + str  
					}).done(function(o) {
						swal({
							title: "Success",
							text: o,
							type: "success"
							}, function(){
							  console.log("success");    
						}); 
					});

					// clean UI
					$(editModalId).modal('toggle');
				}
			});
		},
		template: $("#medicalConditionTemplate").html(),
		replace: true
	}
});

myApp.directive('medicalQuest', function(){
	return {
		scope: {
			model: "=",
			id: "="
		},
		link: function(scope){
			var labels = {
                ailment1: "Diabetes",
				ailment2: "High Blood Pressure",
				ailment3: "Bad Cholestrol",
				ailment4: "Stroke",
                ailment5: "Circulation Problem",
                ailment6: "Bleeding Disorder",
                ailment7: "Cancer",
                ailment8: "Respiratory Problems",
                ailment9: "Rheumatic Fever",
                ailment10: "Kidney Problems",
                ailment11: "Thyroid Prolems",
                ailment12: "HIV",  
                
			};
			
			// models
			angular.extend(scope, {
				labels: labels,
				viewModel: scope.model,
				editModel: {}
			});
			
			// automatically update viewModel if model change
			scope.$watch('model', function(newVal, oldVal){
				scope.viewModel = scope.model;
			});
			
			// methods
			angular.extend(scope, {
				showEditModalFn: function(viewModel, editModalId){
					scope.editModel = viewModel ? angular.copy(viewModel) : {};
					$(editModalId).modal('toggle');
				},
				saveEditFn: function(editModalId){
					// pass data back
					scope.model = angular.copy(scope.editModel);
					var str = jQuery.param( scope.editModel );
					$.ajax({
						type: "GET",
						url: "/update_ailments?" + str
					}).done(function(o) {
						swal({
							title: "Success",
							text: o,
							type: "success"
							}, function(){
							  console.log("success");    
						}); 
					});
					//console.log(scope.editModel);
					// clean UI
					$(editModalId).modal('toggle');
				}
			});
		},
		template: $("#medicalQuestTemplate").html(),
		replace: true
	};
});


myApp.directive('displayText', function(){
	return {
		scope: {
			label: "=",
			model: "="
		},
		template: $("#displayTextTemplate").html(),
		replace: true
	}
});

myApp.directive('formInput', function(){
	return {
		scope: {
			label: "=",
			model: "=",
			type: "@",
			pattern: "@",
			title: "@"
		},
		link: function(scope, element, attributes){
			if (scope.type){ element.find("input").attr("type", scope.type); }
			if (scope.pattern){ element.find("input").attr("pattern", scope.pattern); }
			if (scope.title){ element.find("input").attr("title", scope.title); }
		},
		template: $("#formInputTemplate").html(),
		replace: true
	}
});