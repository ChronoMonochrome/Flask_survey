	// https://stackoverflow.com/questions/5646279/get-object-class-from-string-name-in-javascript
	var _cls_ = {}; // serves as a cache, speed up later lookups
	function getClass(name) {
	    if (!_cls_[name]) {
	        // cache is not ready, fill it up
	        if (name.match(/^[a-zA-Z0-9_.]+$/)) {
	            // proceed only if the name is a single word string
	            _cls_[name] = eval(name);
	        } else {
	            // arbitrary code is detected 
	            throw new Error("Who let the dogs out?");
	        }
	    }
	    return _cls_[name];
	}

	python_to_js = function(columns) {
	    var column_options = ["editor", "formatter", "validator"];

	    var i;
	    for (i = 0; i < columns.length; ++i) {
	        c = columns[i];
	        for (const col_opt of column_options) {
	            if (c[col_opt] === undefined)
	                continue;

	            c[col_opt] = getClass(c[col_opt]);
	        }

	        columns[i] = c;
	    }

	    return columns;
	}